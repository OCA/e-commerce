# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from ..helpers import generate_unique_slug, get_active_saleor_account


class ProductAttribute(models.Model):
    _name = "product.attribute"
    _inherit = ["product.attribute", "mail.thread", "mail.activity.mixin"]

    saleor_slug = fields.Char(help="URL-friendly unique identifier in Saleor")
    saleor_attribute_id = fields.Char(
        string="Saleor Attribute ID", copy=False, index=True, help="ID in Saleor"
    )

    saleor_metadata_line_ids = fields.One2many(
        "saleor.attribute.meta.line", "attribute_id", string="Saleor Metadata"
    )
    saleor_private_metadata_line_ids = fields.One2many(
        "saleor.attribute.private.meta.line",
        "attribute_id",
        string="Saleor Private Metadata",
    )

    _sql_constraints = [
        (
            "saleor_attribute_slug_unique",
            "unique(saleor_slug)",
            "Saleor slug must be unique on product attributes.",
        )
    ]

    def _saleor_prepare_attribute_payload(self):
        self.ensure_one()
        if not self.saleor_slug and self.name:
            self.saleor_slug = generate_unique_slug(
                self, self.name, slug_field_name="saleor_slug"
            )
        payload = {
            "name": self.name,
            "slug": self.saleor_slug,
            # metadata fields
            "metadata": [
                {"key": line.key, "value": line.value}
                for line in self.saleor_metadata_line_ids
            ],
            "privateMetadata": [
                {"key": line.key, "value": line.value}
                for line in self.saleor_private_metadata_line_ids
            ],
        }
        # include current values' names
        values = self.value_ids.mapped("name") if hasattr(self, "value_ids") else []
        payload["values"] = values
        return payload

    def action_saleor_sync(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            rec = self
            payload = rec._saleor_prepare_attribute_payload()
            account.job_attribute_sync(rec.id, payload)
        else:
            # Multiple: batch
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for rec in self:
                payload = rec._saleor_prepare_attribute_payload()
                items.append({"id": rec.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_attribute_sync_batch(chunk)
                else:
                    account.job_attribute_sync_batch(chunk)
        return True
