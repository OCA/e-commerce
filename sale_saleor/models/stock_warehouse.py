# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account, make_link

_logger = logging.getLogger(__name__)


class Warehouse(models.Model):
    _name = "stock.warehouse"
    _inherit = ["stock.warehouse", "mail.thread", "mail.activity.mixin"]

    is_saleor_warehouse = fields.Boolean(
        default=False,
        help="If checked, this warehouse is considered a Saleor warehouse.",
    )

    include_in_saleor_inventory = fields.Boolean(
        default=False,
        help="If checked, stock at this location will be considered\n"
        "when syncing inventory counts to Saleor.",
    )

    saleor_warehouse_id = fields.Char(
        string="Saleor Warehouse ID", copy=False, index=True
    )

    is_private = fields.Selection(
        [
            ("private", "Private Stock"),
            ("public", "Public Stock"),
        ],
        default="private",
        help=(
            "* Private Stock: If enabled stock in this warehouse won't be shown"
            "\n* Public Stock: If enabled stock in this warehouse will be shown"
        ),
    )

    def _saleor_prepare_warehouse_payload(self):
        self.ensure_one()
        # Name rule: name + (short_name). In Odoo, the field code is short name.
        base = self.name or ""
        short = self.code or ""
        name = f"{base} ({short})" if short else base
        partner = self.company_id
        address = {}
        if partner:
            address = {
                "companyName": self.company_id.name,
                "streetAddress1": partner.street or "",
                "streetAddress2": partner.street2 or "",
                "city": partner.city or "",
                "postalCode": (partner.zip or "").strip(),
                "country": partner.country_id.code if partner.country_id else None,
                "countryArea": partner.state_id.name if partner.state_id else "",
                "phone": partner.phone or partner.mobile or "",
            }
        payload = {"name": name}
        if address:
            payload["address"] = address
        return payload

    def action_sync_to_saleor_warehouse(self):
        """
        Sync stock.warehouse to Saleor Warehouse.
        - Single: run immediate
        - Multiple: batch by account.job_batch_size via queue_job
        """
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        # Filter valid records
        records = self.filtered(lambda w: w.is_saleor_warehouse)
        if not records:
            if len(self) == 1:
                raise UserError(
                    _("Enable 'Is Saleor Warehouse' before syncing this warehouse.")
                )
            return True

        if len(records) == 1:
            wh = records
            payload = wh._saleor_prepare_warehouse_payload()
            account.job_warehouse_sync(wh.id, payload)

            base = (account.base_url or "").rstrip("/")
            dash_url = ""
            if base and wh.saleor_warehouse_id:
                dash_url = f"{base}/dashboard/warehouses/{wh.saleor_warehouse_id}"

            link_html = (
                f"<li><b>Saleor</b>: {make_link('View in Saleor', dash_url)}</li>"
                if dash_url
                else ""
            )

            body = (
                "<p><b>Synced warehouse to Saleor</b></p>"
                "<ul>"
                f"<li><b>Account</b>: {account.email or account.name}</li>"
                f"<li><b>Warehouse</b>: {wh.display_name}</li>"
                f"<li><b>Saleor Warehouse ID</b>: {wh.saleor_warehouse_id or ''}</li>"
                f"{link_html}"
                "</ul>"
            )
            wh.message_post(body=body)
            return True

        # Multiple: batch
        batch_size = getattr(account, "job_batch_size", 10) or 10
        items = []
        for wh in records:
            payload = wh._saleor_prepare_warehouse_payload()
            items.append({"id": wh.id, "payload": payload})
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            if hasattr(account, "with_delay"):
                account.with_delay().job_warehouse_sync_batch(chunk)
            else:
                account.job_warehouse_sync_batch(chunk)
        msg = _("Warehouse sync started for %s record(s).", len(records))
        records.message_post(body=msg)
        return True

    def action_sync_product_quantities(self):
        self.ensure_one()
        if not self.include_in_saleor_inventory:
            raise UserError(_("This warehouse is not marked for Saleor sync."))

        account = self.env["saleor.account"].search([("active", "=", True)], limit=1)
        if not account:
            raise UserError(_("No active Saleor account configured."))

        if not self.saleor_warehouse_id:
            raise UserError(_("This warehouse has no linked Saleor warehouse ID."))

        quants = self.env["stock.quant"].search(
            [
                ("location_id", "child_of", self.view_location_id.id),
            ]
        )

        success_count = 0
        skip_count = 0

        for quant in quants:
            product = quant.product_id
            variant_id = product.saleor_variant_id
            if not variant_id:
                skip_count += 1
                continue

            qty = quant.quantity
            account.with_delay().job_variant_stock_update(
                variant_id=variant_id,
                warehouse_id=self.saleor_warehouse_id,
                quantity=qty,
            )
            success_count += 1

        message = _(
            "Successfully updated %(success)s product(s)."
            "\nSkipped %(skip)s product(s) without Saleor Variant ID."
        ) % {
            "success": success_count,
            "skip": skip_count,
        }
        self.message_post(body=message)
        return True

    @api.constrains("is_saleor_warehouse")
    def _check_saleor_warehouse_vs_locations(self):
        for wh in self:
            if not wh.is_saleor_warehouse:
                continue
            has_child_saleor_locations = self.env["stock.location"].search_count(
                [
                    ("warehouse_id", "=", wh.id),
                    ("is_saleor_warehouse", "=", True),
                ]
            )
            if has_child_saleor_locations:
                raise UserError(
                    _(
                        "You cannot mark this warehouse as a Saleor warehouse because "
                        "one or more locations belonging to it"
                        " are already marked as Saleor warehouses."
                    )
                )
