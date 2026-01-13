# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json as _json
import logging

from markupsafe import Markup

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..helpers import generate_unique_slug, get_active_saleor_account, html_to_editorjs

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "mail.thread", "mail.activity.mixin"]

    # Saleor sync fields
    saleor_slug = fields.Char(help="URL-friendly unique identifier in Saleor")
    product_type_id = fields.Many2one(
        "saleor.product.type", string="Saleor Product Type"
    )
    saleor_seo_title = fields.Char(string="Saleor SEO Title")
    saleor_seo_description = fields.Char(string="Saleor SEO Description")
    saleor_product_description = fields.Html(string="Saleor Description (HTML)")
    saleor_product_id = fields.Char(
        string="Saleor Product ID",
        copy=False,
        index=True,
        help="ID of this product in Saleor",
    )

    # Channels linkage
    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_product_template_rel",
        "product_tmpl_id",
        "channel_id",
        string="Channels",
        help="Saleor channels where this product is available.",
    )

    # Optional: link to a collection to sync the product into Saleor collection
    saleor_collection_id = fields.Many2one(
        "product.collection",
        string="Collection",
        help="If set, the product will be added to this Saleor collection during sync.",
    )

    # New requirement
    product_rating = fields.Integer()

    # Track fetch status
    is_metadata_fetched = fields.Boolean(
        string="Metadata Fetched",
        default=False,
        help="Indicates if metadata was successfully fetched from Saleor",
        copy=False,
    )

    # Metadata holders
    saleor_product_metadata_line_ids = fields.One2many(
        "saleor.product.meta.line", "product_tmpl_id", string="Saleor Metadata"
    )

    # Product images
    saleor_image_ids = fields.One2many(
        "saleor.product.image",
        "product_tmpl_id",
        string="Product Images",
        help="Images of the product variant, displayed in the eCommerce.",
    )

    saleor_product_private_metadata_line_ids = fields.One2many(
        "saleor.product.private.meta.line",
        "product_tmpl_id",
        string="Saleor Private Metadata",
    )

    _sql_constraints = [
        (
            "saleor_slug_unique",
            "unique(saleor_slug)",
            "Saleor slug must be unique on products.",
        )
    ]

    def _saleor_prepare_payload(self):
        self.ensure_one()
        if not self.saleor_slug and self.name:
            self.saleor_slug = generate_unique_slug(
                self, self.name, slug_field_name="saleor_slug"
            )
        payload = {
            # Store the current image IDs to track deleted images
            "_saleor_current_image_ids": self.saleor_image_ids.filtered(
                "saleor_image_id"
            ).mapped("saleor_image_id"),
            "name": self.name,
            "slug": self.saleor_slug,
        }
        # Saleor expects JSONString, i.e., a JSON-encoded string, not a dict
        if self.saleor_product_description:
            desc = html_to_editorjs(self.saleor_product_description)
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
            # Collect Saleor channel IDs and ensure every selected channel is synced
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

        # Map metadata lines
        meta_lines = self.saleor_product_metadata_line_ids
        payload["metadata"] = (
            [{"key": line.key, "value": line.value} for line in meta_lines]
            if meta_lines
            else []
        )
        priv_lines = self.saleor_product_private_metadata_line_ids
        payload["privateMetadata"] = (
            [{"key": line.key, "value": line.value} for line in priv_lines]
            if priv_lines
            else []
        )

        # Map product_rating to Saleor 'rating' field
        if self.product_rating is not None:
            try:
                payload["rating"] = int(self.product_rating)
            except Exception as e:
                _logger.warning(
                    "Saleor product rating is non-numeric for product %s: %r (%s)",
                    self.display_name,
                    self.product_rating,
                    e,
                )
                payload["rating"] = self.product_rating

        return payload

    def action_saleor_sync(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        # If only one record selected, run immediate (no queue)
        if len(self) == 1:
            tmpl = self
            payload = tmpl._saleor_prepare_payload()
            account.job_product_sync(tmpl.id, payload)
        else:
            # Multiple records: batch into groups
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for tmpl in self:
                payload = tmpl._saleor_prepare_payload()
                items.append({"id": tmpl.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_product_sync_batch(chunk)
                else:
                    account.job_product_sync_batch(chunk)
        return True

    def write(self, vals):
        res = super().write(vals)
        # When attributes matrix changes, resync variants with Saleor
        if "attribute_line_ids" in vals:
            account = get_active_saleor_account(self.env, raise_if_missing=False)
            if account:
                templates = self.filtered(lambda t: t.saleor_product_id)
                for tmpl in templates:
                    # Post chatter note about attribute change and resync
                    try:
                        variants = tmpl.product_variant_ids
                        variant_lines = []
                        for v in variants:
                            # Collect attribute values if available
                            values = getattr(
                                v,
                                "product_template_attribute_value_ids",
                                self.env["product.template.attribute.value"],
                            )
                            if values:
                                vals_str = ", ".join(values.mapped("name"))
                                variant_lines.append(
                                    f"<li><b>Variant</b>: {v.display_name}"
                                    f" — {vals_str}</li>"
                                )
                            else:
                                variant_lines.append(
                                    f"<li><b>Variant</b>: {v.display_name}</li>"
                                )
                        variants_html = "".join(variant_lines) if variant_lines else ""
                        body = (
                            "<p>Product attributes changed; "
                            "queued Saleor variants resync.</p>"
                            "<ul class='mb-0 ps-4'>"
                            f"<li><b>Template</b>: {tmpl.display_name}</li>"
                            "</ul>"
                        )
                        if variants_html:
                            body += "<ul class='mb-0 ps-4'>" f"{variants_html}" "</ul>"
                        tmpl.message_post(body=Markup(body))
                    except Exception as e:
                        _logger.warning(
                            "Failed to post attribute change note for %s: %s",
                            tmpl.display_name,
                            e,
                        )
                    try:
                        if hasattr(account, "with_delay"):
                            account.with_delay().job_product_variants_resync(tmpl.id)
                        else:
                            account.job_product_variants_resync(tmpl.id)
                    except Exception as e:
                        _logger.warning(
                            "Failed to enqueue Saleor variants resync for %s: %s",
                            tmpl.display_name,
                            e,
                        )
        return res

    def action_fetch_metadata(self):
        """Fetch metadata and private metadata from selected Saleor account.

        For single record, process immediately. For multiple records, use queue_job.
        """
        # Resolve the single active Saleor account
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        # For a single record, process immediately
        if len(self) == 1:
            self.write({"is_metadata_fetched": False})
            success = account.job_product_metadata_fetch(self.id)
            if success:
                _logger.info("Successfully fetched metadata from %s", account.name)
            return success

        # For multiple records, use queue_job if available
        self.write({"is_metadata_fetched": False})
        if hasattr(account, "with_delay"):
            account.with_delay().job_saleor_fetch(self.ids, self._name)
        else:
            account.job_saleor_fetch(self.ids, self._name)

        _logger.info(
            "Started fetching metadata for %s products from %s in the background",
            len(self),
            account.name,
        )
        return True

    def _notify_saleor_sync(self, warehouse, success=True, error_msg=None):
        """Notify sync result in chatter"""
        if success:
            body = (
                "<p>Updated stock in Saleor:</p>"
                "<ul class='mb-0 ps-4'>"
                f"<li><b>Product</b>: {self.display_name}</li>"
                f"<li><b>Warehouse</b>: {warehouse.display_name}</li>"
                "</ul>"
            )
        else:
            error_text = error_msg or _("Unknown error")
            body = (
                "<p>Failed to update stock in Saleor:</p>"
                "<ul class='mb-0 ps-4'>"
                f"<li><b>Product</b>: {self.display_name}</li>"
                f"<li><b>Warehouse</b>: {warehouse.display_name}</li>"
                f"<li><b>Reason</b>: {error_text}</li>"
                "</ul>"
            )
        self.message_post(body=Markup(body))

    def action_sync_product_quantities(self):  # noqa: C901
        account = get_active_saleor_account(self.env, raise_if_missing=True)

        saleor_warehouses = self.env["stock.warehouse"].search(
            [
                ("is_saleor_warehouse", "=", True),
                ("include_in_saleor_inventory", "=", True),
            ]
        )
        saleor_locations = self.env["stock.location"].search(
            [
                ("is_saleor_warehouse", "=", True),
                ("include_in_saleor_inventory", "=", True),
            ]
        )

        if not saleor_warehouses and not saleor_locations:
            raise UserError(_("No warehouses or locations marked for Saleor sync."))

        # Collect all variants with Saleor IDs across selected templates
        variants = self.mapped("product_variant_ids")
        missing = variants.filtered(lambda v: not v.saleor_variant_id)
        for v in missing:
            reason_text = _("Does not have a Saleor Variant ID")
            body = (
                "<p>Variant skipped during inventory synchronization:</p>"
                "<ul class='mb-0 ps-4'>"
                f"<li><b>Variant</b>: {v.display_name}</li>"
                f"<li><b>Reason</b>: {reason_text}</li>"
                "</ul>"
            )
            v.product_tmpl_id.message_post(body=Markup(body))

        variants = variants - missing
        if not variants:
            return True

        variant_by_id = {v.id: v for v in variants}
        variant_ids = list(variant_by_id.keys())
        Quant = self.env["stock.quant"].sudo()

        # Batch by warehouses using _read_group
        def _push_qty(prod, warehouse_id, qty, target):
            qty = qty or 0.0
            try:
                if hasattr(account, "with_delay"):
                    account.with_delay().job_variant_stock_update(
                        variant_id=prod.saleor_variant_id,
                        warehouse_id=warehouse_id,
                        quantity=qty,
                    )
                else:
                    account.job_variant_stock_update(
                        variant_id=prod.saleor_variant_id,
                        warehouse_id=warehouse_id,
                        quantity=qty,
                    )
                prod._notify_saleor_sync(target, success=True)
            except Exception as e:
                prod._notify_saleor_sync(target, success=False, error_msg=str(e))

        for wh in saleor_warehouses:
            domain = [
                ("location_id", "child_of", wh.view_location_id.id),
                ("product_id", "in", variant_ids),
            ]
            rows = Quant.read_group(
                domain,
                ["quantity:sum"],
                ["product_id"],
            )
            for row in rows:
                product_group = row.get("product_id")
                prod_id = product_group and product_group[0]
                if not prod_id:
                    continue
                prod = variant_by_id.get(prod_id)
                if not prod:
                    continue
                qty = row.get("quantity") or 0.0
                _push_qty(prod, wh.saleor_warehouse_id, qty, wh)

        # Batch by exact locations using _read_group
        for loc in saleor_locations:
            domain = [("location_id", "=", loc.id), ("product_id", "in", variant_ids)]
            rows = Quant.read_group(
                domain,
                ["quantity:sum"],
                ["product_id"],
            )
            for row in rows:
                product_group = row.get("product_id")
                prod_id = product_group and product_group[0]
                if not prod_id:
                    continue
                prod = variant_by_id.get(prod_id)
                if not prod:
                    continue
                qty = row.get("quantity") or 0.0
                _push_qty(prod, loc.saleor_warehouse_id, qty, loc)

        # Post completion messages per template
        for template in self:
            body = (
                "<p>Successfully synchronized inventory for template:</p>"
                "<ul class='mb-0 ps-4'>"
                f"<li><b>Template</b>: {template.display_name}</li>"
                "</ul>"
            )
            template.message_post(body=Markup(body))
