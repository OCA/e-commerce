import json as _json

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..helpers import generate_unique_slug, get_active_saleor_account, html_to_editorjs


class ProductCollection(models.Model):
    _name = "product.collection"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product Collection"

    name = fields.Char(required=True)
    saleor_collection_id = fields.Char(
        string="Saleor Collection ID",
        copy=False,
        index=True,
        help="ID of this collection in Saleor",
    )
    saleor_collection_slug = fields.Char(
        help="URL-friendly unique identifier in Saleor"
    )
    saleor_collection_description = fields.Html(string="Saleor Description (HTML)")
    saleor_collection_seo_title = fields.Char(string="Saleor SEO Title")
    saleor_collection_seo_description = fields.Char(string="Saleor SEO Description")
    saleor_collection_metadata_line_ids = fields.One2many(
        "saleor.collection.meta.line",
        "collection_id",
    )
    saleor_collection_private_metadata_line_ids = fields.One2many(
        "saleor.collection.private.meta.line", "collection_id"
    )
    saleor_background_image = fields.Binary()

    sync_to_saleor = fields.Boolean(
        string="Sync to Saleor",
        default=False,
        help=(
            "If unchecked, this collection will not be synchronized with Saleor, "
            "including metadata and channel availability."
        ),
    )

    _sql_constraints = [
        (
            "saleor_collection_slug_unique",
            "unique(saleor_collection_slug)",
            "Saleor slug must be unique on collections.",
        )
    ]

    # Channels linkage
    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_product_collection_rel",
        "collection_id",
        "channel_id",
        string="Channels",
        help="Saleor channels where this collection is available.",
    )

    def _saleor_collection_prepare_payload(self):
        self.ensure_one()
        name = self.name

        if not self.saleor_collection_slug and name:
            self.saleor_collection_slug = generate_unique_slug(
                self, name, slug_field_name="saleor_collection_slug"
            )

        payload = {
            "name": name,
            "slug": self.saleor_collection_slug,
        }
        # Saleor expects JSONString, i.e., a JSON-encoded string, not a dict
        if self.saleor_collection_description:
            desc = html_to_editorjs(self.saleor_collection_description)
            if desc is not None:
                payload["description"] = _json.dumps(desc)
        seo = {}
        if self.saleor_collection_seo_title:
            seo["title"] = self.saleor_collection_seo_title
        if self.saleor_collection_seo_description:
            seo["description"] = self.saleor_collection_seo_description
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

        # Map Odoo lines to Saleor metadata fields
        meta_lines = self.saleor_collection_metadata_line_ids
        payload["metadata"] = (
            [{"key": line.key, "value": line.value} for line in meta_lines]
            if meta_lines
            else []
        )
        priv_lines = self.saleor_collection_private_metadata_line_ids
        payload["privateMetadata"] = (
            [{"key": line.key, "value": line.value} for line in priv_lines]
            if priv_lines
            else []
        )
        return payload

    def action_saleor_collection_sync(self):
        # Sync selected collections to all active Saleor accounts
        invalid = self.filtered(lambda col: not col.sync_to_saleor)
        if invalid:
            names = "\n- " + "\n- ".join(invalid.mapped("display_name"))
            raise UserError(
                _(
                    "Please enable 'Sync to Saleor' on the following collections "
                    "before running Saleor synchronization:%s",
                    names,
                )
            )

        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            col = self
            payload = col._saleor_collection_prepare_payload()
            account.job_collection_sync(col.id, payload)
        else:
            # Multiple: batch
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for col in self:
                payload = col._saleor_collection_prepare_payload()
                items.append({"id": col.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_collection_sync_batch(chunk)
                else:
                    account.job_collection_sync_batch(chunk)
        return True
