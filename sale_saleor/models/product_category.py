import json as _json

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..helpers import generate_unique_slug, get_active_saleor_account, html_to_editorjs


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "mail.thread", "mail.activity.mixin"]

    saleor_slug = fields.Char(help="URL-friendly unique identifier in Saleor")
    saleor_description = fields.Html(string="Saleor Description (HTML)")
    saleor_seo_title = fields.Char(string="Saleor SEO Title")
    saleor_seo_description = fields.Char(string="Saleor SEO Description")
    saleor_category_id = fields.Char(
        string="Saleor Category ID",
        copy=False,
        index=True,
        help="ID of this category in Saleor",
    )
    saleor_metadata_line_ids = fields.One2many(
        "saleor.category.meta.line",
        "category_id",
    )
    saleor_private_metadata_line_ids = fields.One2many(
        "saleor.category.private.meta.line", "category_id"
    )
    saleor_background_image = fields.Binary()

    _sql_constraints = [
        (
            "saleor_category_slug_unique",
            "unique(saleor_slug)",
            "Saleor slug must be unique on categories.",
        )
    ]

    # Channels linkage
    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_product_category_rel",
        "category_id",
        "channel_id",
        string="Channels",
        help="Saleor channels where this category is available.",
    )

    def _saleor_prepare_payload(self):
        self.ensure_one()
        name = self.name

        if not self.saleor_slug and name:
            self.saleor_slug = generate_unique_slug(
                self, name, slug_field_name="saleor_slug"
            )

        payload = {
            "name": name,
            "slug": self.saleor_slug,
        }
        # Saleor expects JSONString, i.e., a JSON-encoded string, not a dict
        if self.saleor_description:
            desc = html_to_editorjs(self.saleor_description)
            if desc is not None:
                payload["description"] = _json.dumps(desc)
        seo = {}
        if self.saleor_seo_title:
            seo["title"] = self.saleor_seo_title
        if self.saleor_seo_description:
            seo["description"] = self.saleor_seo_description
        if seo:
            payload["seo"] = seo
        # Channels
        if self.channel_ids:
            channel_saleor_ids = [
                ch.saleor_channel_id for ch in self.channel_ids if ch.saleor_channel_id
            ]
            missing = [
                ch.display_name for ch in self.channel_ids if not ch.saleor_channel_id
            ]
            if missing:
                raise UserError(
                    _(
                        "Please sync the following channels to Saleor first: %s",
                        ", ".join(missing),
                    )
                )
            if channel_saleor_ids:
                payload["addChannels"] = channel_saleor_ids
        # Parent linkage: if parent has a stored Saleor ID, reference it
        parent_saleor_id = self.parent_id and self.parent_id.saleor_category_id or False
        if parent_saleor_id:
            payload["parent"] = parent_saleor_id
        # Map Odoo lines to Saleor metadata fields
        meta_lines = self.saleor_metadata_line_ids
        payload["metadata"] = (
            [{"key": line.key, "value": line.value} for line in meta_lines]
            if meta_lines
            else []
        )
        priv_lines = self.saleor_private_metadata_line_ids
        payload["privateMetadata"] = (
            [{"key": line.key, "value": line.value} for line in priv_lines]
            if priv_lines
            else []
        )
        return payload

    def action_saleor_sync(self):
        # Sync this category to all active Saleor accounts
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            cat = self
            payload = cat._saleor_prepare_payload()
            account.job_category_sync(cat.id, payload)
        else:
            # Batch multi records
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for cat in self:
                payload = cat._saleor_prepare_payload()
                items.append({"id": cat.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_category_sync_batch(chunk)
                else:
                    account.job_category_sync_batch(chunk)
        return True
