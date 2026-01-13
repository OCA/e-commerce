# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class SaleorChannel(models.Model):
    _name = "saleor.channel"
    _description = "Saleor Channel"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    slug = fields.Char(
        required=True, tracking=True, help="Unique channel slug in Saleor"
    )
    status = fields.Selection(
        selection=[("inactive", "Inactive"), ("active", "Active")],
        default="inactive",
        required=True,
        tracking=True,
    )
    currency_id = fields.Many2one("res.currency", string="Currency", required=True)
    default_country_id = fields.Many2one(
        "res.country", string="Default Country", required=True
    )
    shipping_zone_ids = fields.Many2many(
        "saleor.shipping.zone",
        "saleor_channel_shipping_zone_rel",
        "channel_id",
        "shipping_zone_id",
        string="Shipping Zone",
        help="Assign one or more Saleor shipping zones to this channel.",
    )

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        "saleor_channel_warehouse_rel",
        "channel_id",
        "warehouse_id",
        string="Warehouses",
        domain=[("is_saleor_warehouse", "=", True)],
        help="Only warehouses marked as Saleor warehouses are allowed.",
    )
    location_ids = fields.Many2many(
        "stock.location",
        "saleor_channel_location_rel",
        "channel_id",
        "location_id",
        string="Locations",
        domain=[("is_saleor_warehouse", "=", True), ("usage", "=", "internal")],
        help="Only internal locations marked as Saleor warehouses are allowed.",
    )

    saleor_channel_id = fields.Char(readonly=True, copy=False, index=True)
    entered_prices = fields.Selection(
        selection=[
            ("with_tax", "Product prices are entered with tax"),
            ("without_tax", "Product prices are entered without tax"),
        ],
        default="without_tax",
    )
    abandoned_cart_delay_hours = fields.Float(
        string="Abandoned Cart Delay (Hours)",
        help=(
            "For orders imported from this Saleor channel, quotations that stay in "
            "draft/sent state longer than this delay will be marked as abandoned."
        ),
        default=24.0,
    )

    _sql_constraints = [
        ("slug_unique", "unique(slug)", "Channel slug must be unique."),
    ]

    @api.model
    def cron_mark_abandoned_saleor_orders(self):
        """Mark old Saleor quotations as abandoned based on channel delay."""
        SaleOrder = self.env["sale.order"].sudo()
        now = fields.Datetime.now()
        # Candidate orders: Saleor-origin quotations that are still open.
        orders = SaleOrder.search(
            [
                ("saleor_order_id", "!=", False),
                ("state", "in", ("draft")),
                ("is_abandoned", "=", False),
            ]
        )
        if not orders:
            return

        to_abandon = self.env["sale.order"].sudo()
        for order in orders:
            channel = getattr(order, "saleor_channel_id", False)
            delay = getattr(channel, "abandoned_cart_delay_hours", 0.0) or 0.0
            # Skip if no delay configured on the channel
            if not delay:
                continue
            cutoff = now - relativedelta(hours=delay)
            # Use date_order if available, otherwise fall back to create_date
            order_date = order.date_order or order.create_date
            if order_date and order_date <= cutoff:
                to_abandon |= order

        if to_abandon:
            _logger.info(
                "Marking %s Saleor quotations as abandoned (per-channel delay)",
                len(to_abandon),
            )
            to_abandon.write({"is_abandoned": True})
            for order in to_abandon:
                channel = getattr(order, "saleor_channel_id", False)
                delay = getattr(channel, "abandoned_cart_delay_hours", 0.0) or 0.0
                try:
                    order.message_post(
                        body=_(
                            "This quotation has been marked as abandoned by the "
                            "Saleor connector cron (delay=%s hours).",
                            delay,
                        )
                    )
                except Exception:
                    # Never block the cron on chatter issues
                    _logger.debug(
                        "Failed to post abandoned-cart message on sale.order %s",
                        order.id,
                    )

    def _prepare_saleor_payload(self, include_currency=True):
        self.ensure_one()
        payload = {
            "name": self.name,
            "slug": self.slug,
            "isActive": self.status == "active",
            "defaultCountry": (self.default_country_id and self.default_country_id.code)
            or None,
        }
        if include_currency:
            payload["currencyCode"] = self.currency_id.name

        # Warehouses/Locations: add addWarehouses with Saleor IDs
        selected_wh = self.warehouse_ids or self.env["stock.warehouse"]
        selected_loc = self.location_ids or self.env["stock.location"]
        wh_ids = [
            wh.saleor_warehouse_id for wh in selected_wh if wh.saleor_warehouse_id
        ]
        loc_ids = [
            loc.saleor_warehouse_id for loc in selected_loc if loc.saleor_warehouse_id
        ]
        # Validate that every selected has a Saleor ID
        missing = []
        missing += [wh.display_name for wh in selected_wh if not wh.saleor_warehouse_id]
        missing += [
            loc.display_name for loc in selected_loc if not loc.saleor_warehouse_id
        ]
        if missing:
            raise UserError(
                _(
                    "Please sync the following warehouses/locations"
                    " to Saleor first: %s",
                    ", ".join(missing),
                )
            )
        add_warehouses = [*wh_ids, *loc_ids]
        if add_warehouses:
            payload["addWarehouses"] = add_warehouses
        return payload

    def action_sync_to_saleor(self):
        """Sync channels to Saleor."""
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            payload = self._prepare_saleor_payload(
                include_currency=not bool(self.saleor_channel_id)
            )
            account.job_channel_sync(self.id, payload)
            return True

        # Multiple: batch
        batch_size = getattr(account, "job_batch_size", 10) or 10
        items = []
        for rec in self:
            payload = rec._prepare_saleor_payload(
                include_currency=not bool(rec.saleor_channel_id)
            )
            items.append({"id": rec.id, "payload": payload})
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            if hasattr(account, "with_delay"):
                account.with_delay().job_channel_sync_batch(chunk)
            else:
                account.job_channel_sync_batch(chunk)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Auto-sync all records created as active
        active_records = records.filtered(lambda r: r.status == "active")
        if active_records:
            active_records.action_sync_to_saleor()
        return records

    def write(self, vals):
        # Disallow changing currency after the channel has been synced to Saleor
        if "currency_id" in vals:
            for rec in self:
                if rec.saleor_channel_id and not self.env.context.get(
                    "bypass_currency_lock"
                ):
                    raise UserError(
                        _(
                            "Currency cannot be changed after the channel"
                            " has been synced to Saleor."
                        )
                    )
        res = super().write(vals)
        # If status toggled to active, sync now;
        # or if already active and key fields changed
        fields_affecting = {
            "name",
            "slug",
            "status",
            "currency_id",
            "default_country_id",
        }
        for rec in self:
            status_target = vals.get("status")
            should_sync = False
            if status_target == "active":
                should_sync = True
            elif rec.status == "active" and fields_affecting.intersection(vals.keys()):
                should_sync = True
            if should_sync:
                rec.action_sync_to_saleor()
        return res
