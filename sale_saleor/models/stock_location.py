# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account, make_link

_logger = logging.getLogger(__name__)


class Location(models.Model):
    _name = "stock.location"
    _inherit = ["stock.location", "mail.thread", "mail.activity.mixin"]

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        help="Warehouse this location belongs to (used by Saleor integration)",
    )

    is_saleor_warehouse = fields.Boolean(
        default=False,
        help="If checked, this location is considered a Saleor warehouse.",
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
            "* Private Stock: If enabled stock in this location won't be shown"
            "\n*Public Stock: If enabled stock in this location will be shown"
        ),
    )

    def _saleor_prepare_warehouse_payload(self):
        self.ensure_one()
        # Name rule for locations: use complete_name
        name = self.complete_name or self.name
        partner = self.company_id
        address = {}
        if partner:
            # Sanitize phone for Saleor: keep leading '+' and digits
            def _sanitize_phone(val):
                if not val:
                    return None
                s = "".join(ch for ch in str(val) if ch.isdigit() or ch == "+")
                if s.count("+") > 1:
                    s = "+" + s.replace("+", "")
                digits_len = sum(1 for ch in s if ch.isdigit())
                if digits_len < 7 or digits_len > 15:
                    return None
                return s

            phone_val = partner.phone or partner.mobile or ""
            phone_clean = _sanitize_phone(phone_val)

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
            if phone_clean:
                address["phone"] = phone_clean
        payload = {"name": name}
        if address:
            payload["address"] = address
        return payload

    def action_sync_to_saleor_warehouse(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        # Validate and filter
        records = self.filtered(lambda loc: loc.is_saleor_warehouse)
        if not records:
            if len(self) == 1:
                raise UserError(
                    _("Enable 'Is Saleor Warehouse'" " before syncing this location.")
                )
            return True

        # Single: run immediate
        if len(records) == 1:
            loc = records
            payload = loc._saleor_prepare_warehouse_payload()
            account.job_location_sync(loc.id, payload)

            base = (account.base_url or "").rstrip("/")
            dash_url = ""
            if base and loc.saleor_warehouse_id:
                dash_url = f"{base}/dashboard/warehouses/{loc.saleor_warehouse_id}"

            link_html = (
                f"<li><b>Saleor</b>: {make_link('View in Saleor', dash_url)}</li>"
                if dash_url
                else ""
            )

            body = (
                "<p><b>Synced location to Saleor</b></p>"
                "<ul>"
                f"<li><b>Account</b>: {account.email or account.name}</li>"
                f"<li><b>Location</b>: {loc.display_name}</li>"
                f"<li><b>Saleor Warehouse ID</b>: {loc.saleor_warehouse_id or ''}</li>"
                f"{link_html}"
                "</ul>"
            )
            loc.message_post(body=body)
            return True

        # Multiple: batch
        batch_size = getattr(account, "job_batch_size", 10) or 10
        items = []
        for loc in records:
            payload = loc._saleor_prepare_warehouse_payload()
            items.append({"id": loc.id, "payload": payload})
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            if hasattr(account, "with_delay"):
                account.with_delay().job_location_sync_batch(chunk)
            else:
                account.job_location_sync_batch(chunk)
        msg = _("Location sync started for %s record(s).") % len(records)
        records.message_post(body=msg)
        return True

    def action_sync_product_quantities(self):
        """
        Update stock for a product variant in Saleor.
        """
        self.ensure_one()
        if not self.include_in_saleor_inventory:
            raise UserError(_("This location is not marked for Saleor sync."))

        account = get_active_saleor_account(self.env, raise_if_missing=True)

        if not self.saleor_warehouse_id:
            raise UserError(_("This location has no linked Saleor warehouse ID."))

        quants = self.env["stock.quant"].search([("location_id", "=", self.id)])
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

    @api.constrains("is_saleor_warehouse", "warehouse_id")
    def _check_saleor_location_vs_warehouse(self):
        for loc in self:
            if (
                loc.is_saleor_warehouse
                and loc.warehouse_id
                and loc.warehouse_id.is_saleor_warehouse
            ):
                raise UserError(
                    _(
                        "You cannot mark this location as a Saleor warehouse because"
                        " its warehouse (%s) is already marked as a Saleor warehouse.",
                        loc.warehouse_id.display_name,
                    )
                )
