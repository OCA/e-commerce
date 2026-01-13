# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class SaleorShippingZone(models.Model):
    _name = "saleor.shipping.zone"
    _description = "Saleor Shipping Zone"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    saleor_id = fields.Char(string="Saleor ID", copy=False, index=True)
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()

    country_ids = fields.Many2many(
        "res.country",
        "saleor_shipping_zone_country_rel",
        "zone_id",
        "country_id",
        string="Assigned Countries",
    )

    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_shipping_zone_rel",
        "shipping_zone_id",
        "channel_id",
        string="Channels",
    )

    warehouse_ids = fields.Many2many(
        "stock.warehouse",
        "saleor_shipping_zone_warehouse_rel",
        "zone_id",
        "warehouse_id",
        string="Warehouses",
        domain=[("is_saleor_warehouse", "=", True)],
        help="Only warehouses marked as Saleor warehouses are allowed.",
    )
    location_ids = fields.Many2many(
        "stock.location",
        "saleor_shipping_zone_location_rel",
        "zone_id",
        "location_id",
        string="Locations",
        domain=[("is_saleor_warehouse", "=", True), ("usage", "=", "internal")],
        help="Only internal locations marked as Saleor warehouses are allowed.",
    )

    shipping_method_ids = fields.Many2many(
        "delivery.carrier",
        "saleor_shipping_zone_shipping_method_rel",
        "shipping_zone_id",
        "shipping_method_id",
        string="Shipping Methods",
    )

    # Metadata for Shipping Zone
    shipping_zone_metadata_line_ids = fields.One2many(
        "shipping.zone.meta.line", "zone_id", string="Metadata"
    )
    shipping_zone_private_metadata_line_ids = fields.One2many(
        "shipping.zone.private.meta.line", "zone_id", string="Private Metadata"
    )

    def _update_carriers_zone_link(self):
        """Force-link carriers' zone_id to this zone when related here."""
        for zone in self:
            carriers = zone.shipping_method_ids.filtered(
                lambda c: c.delivery_type == "saleor"
            )
            if carriers:
                carriers_to_update = carriers.filtered(
                    lambda c, zid=zone.id: c.zone_id.id != zid
                )
                if carriers_to_update:
                    carriers_to_update.write({"zone_id": zone.id})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        zones_with_methods = records.filtered(
            lambda zone: bool(zone.shipping_method_ids)
        )
        if zones_with_methods:
            zones_with_methods._update_carriers_zone_link()
        return records

    def write(self, vals):
        res = super().write(vals)
        # If shipping methods changed, align carriers' zone_id
        if vals.get("shipping_method_ids"):
            self._update_carriers_zone_link()
        return res

    def _saleor_shipping_zone_prepare_payload(self):
        """Build payload for Saleor shipping zone create/update."""
        self.ensure_one()
        payload = {
            "name": self.name,
            "description": self.description or "",
            "countries": [c.code for c in self.country_ids],
            "addChannels": [
                c.saleor_channel_id for c in self.channel_ids if c.saleor_channel_id
            ],
        }

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

        # Metadata and private metadata
        meta = [
            {"key": line.key, "value": line.value}
            for line in (self.shipping_zone_metadata_line_ids or [])
        ]
        priv = [
            {"key": line.key, "value": line.value}
            for line in (self.shipping_zone_private_metadata_line_ids or [])
        ]
        if meta:
            payload["metadata"] = meta
        if priv:
            payload["privateMetadata"] = priv

        return payload

    def action_saleor_shipping_zone_sync(self):
        """Sync shipping zones to Saleor (direct if single, queue if multi)."""
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        if len(self) == 1:
            zone = self
            payload = zone._saleor_shipping_zone_prepare_payload()
            account.job_shipping_zone(zone.id, payload)
        else:
            # Multiple: batch
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for zone in self:
                payload = zone._saleor_shipping_zone_prepare_payload()
                items.append({"id": zone.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_shipping_zone_batch(chunk)
                else:
                    account.job_shipping_zone_batch(chunk)
        return True
