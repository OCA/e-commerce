# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account


class AccountTax(models.Model):
    _inherit = "account.tax"

    saleor_metadata_line_ids = fields.One2many(
        "saleor.tax.meta.line",
        "tax_id",
        string="Saleor Metadata",
    )
    saleor_private_metadata_line_ids = fields.One2many(
        "saleor.tax.private.meta.line",
        "tax_id",
        string="Saleor Private Metadata",
    )

    # Store Saleor TaxClass ID
    saleor_tax_class_id = fields.Char(
        string="Saleor TaxClass ID", copy=False, index=True, help="ID in Saleor"
    )

    def _saleor_prepare_tax_payload(self):
        self.ensure_one()
        if self.amount_type != "percent" or self.type_tax_use != "sale":
            raise UserError(
                self.env._("Only percent Sales taxes can be synced to Saleor TaxClass.")
            )

        # Base payload
        payload = {
            "name": self.name,
        }

        # Metadata
        meta = [
            {"key": line.key, "value": line.value}
            for line in (self.saleor_metadata_line_ids or [])
        ]
        priv = [
            {"key": line.key, "value": line.value}
            for line in (self.saleor_private_metadata_line_ids or [])
        ]
        if meta:
            payload["metadata"] = meta
        if priv:
            payload["privateMetadata"] = priv

        # Country rates: prefer the tax's country if set, otherwise fallback to company
        country = (
            getattr(self, "country_id", False)
            or getattr(self.company_id, "country_id", False)
            or getattr(self.env.company, "country_id", False)
        )
        country_code = getattr(country, "code", None)
        if country_code:
            payload["createCountryRates"] = [
                {"countryCode": country_code, "rate": float(self.amount or 0.0)}
            ]
        return payload

    def _saleor_validate_tax_for_sync(self):
        self.ensure_one()
        if self.amount_type != "percent" or self.type_tax_use != "sale":
            raise UserError(
                self.env._("Only percent Sales taxes can be synced to Saleor TaxClass.")
            )

    def action_saleor_tax_sync(self):
        """Sync this tax to Saleor as a TaxClass."""
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        if len(self) == 1:
            tax = self
            tax._saleor_validate_tax_for_sync()
            payload = tax._saleor_prepare_tax_payload()
            account.job_tax_sync(tax.id, payload)
        else:
            # Multiple: batch
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for tax in self:
                tax._saleor_validate_tax_for_sync()
                payload = tax._saleor_prepare_tax_payload()
                items.append({"id": tax.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_tax_sync_batch(chunk)
                else:
                    account.job_tax_sync_batch(chunk)
        return True
