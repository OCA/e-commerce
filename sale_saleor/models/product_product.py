# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from markupsafe import Markup

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "mail.thread", "mail.activity.mixin"]

    # Saleor sync fields
    saleor_variant_id = fields.Char(
        string="Saleor Variant ID",
        copy=False,
        index=True,
        help="ID of this product variant in Saleor",
    )
    # Variant-level channels (override template channels if set)
    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_product_product_rel",
        "product_id",
        "channel_id",
        help=(
            "Saleor channels where this variant is available."
            " Overrides template channels if set."
        ),
    )
    saleor_sku = fields.Char(
        string="Saleor SKU",
        related="default_code",
        store=True,
        readonly=False,
        help="""
        This field is synchronized with the default_code (Internal Reference) field
        """,
    )
    sync_to_saleor = fields.Boolean(
        string="Sync to Saleor",
        default=False,
        help=(
            "If unchecked, synchronization of this variant with Saleor "
            "(including inventory updates) will be disabled."
        ),
    )

    def _variant_add_channels(self, payload):
        def _collect_channels(recs):
            ids_ = [ch.saleor_channel_id for ch in recs if ch.saleor_channel_id]
            miss = [ch.display_name for ch in recs if not ch.saleor_channel_id]
            return ids_, miss

        variant_channels = getattr(self, "channel_ids", False) and self.channel_ids
        if variant_channels:
            channel_saleor_ids, missing = _collect_channels(variant_channels)
            if missing:
                raise UserError(
                    _(
                        "Please sync the following channels to Saleor first: %s",
                        ", ".join(missing),
                    )
                )
            if channel_saleor_ids:
                payload["addChannels"] = channel_saleor_ids
        else:
            tmpl = self.product_tmpl_id
            if getattr(tmpl, "channel_ids", False) and tmpl.channel_ids:
                channel_saleor_ids, missing = _collect_channels(tmpl.channel_ids)
                if missing:
                    raise UserError(
                        _(
                            "Please sync the following channels to Saleor first: %s",
                            ", ".join(missing),
                        )
                    )
                if channel_saleor_ids:
                    payload["addChannels"] = channel_saleor_ids

    def _variant_add_cost_price(self, payload):
        try:
            currency_code = self.product_tmpl_id.currency_id.name
            if currency_code and self.standard_price is not None:
                payload["costPrice"] = {
                    "amount": float(self.standard_price),
                    "currency": currency_code,
                }
        except Exception as e:
            _logger.debug(
                "Saleor: skip costPrice mapping for %s: %s",
                self.display_name,
                e,
            )

    def _variant_add_channel_listings(self, payload):
        try:
            ch_ids = payload.get("addChannels") or []
            if not ch_ids:
                return
            preferred = (
                self.channel_ids
                or getattr(self.product_tmpl_id, "channel_ids", False)
                and self.product_tmpl_id.channel_ids
                or self.env["saleor.channel"]
            )
            by_saleor_id = {
                ch.saleor_channel_id: ch for ch in preferred if ch.saleor_channel_id
            }
            listings = []
            for cid in ch_ids:
                ch = by_saleor_id.get(cid)
                if not ch:
                    continue
                listings.append(
                    {
                        "channelId": cid,
                        # Saleor expects PositiveDecimal (string)
                        "price": str(float(self.lst_price or 0.0)),
                    }
                )
            if listings:
                payload["channelListings"] = listings
        except Exception as e:
            _logger.debug(
                "Saleor: skip channelListings build for %s: %s",
                self.display_name,
                e,
            )

    def _variant_add_weight(self, payload):
        try:
            weight_val = float(self.weight or 0.0)
            if weight_val > 0:
                payload["weight"] = weight_val
        except Exception as e:
            _logger.debug(
                "Saleor: skip weight mapping for %s: %s",
                self.display_name,
                e,
            )

    def _saleor_prepare_variant_payload(self, product_id):
        """Prepare the payload for syncing a product variant to Saleor."""
        self.ensure_one()
        payload = {
            "product": product_id,
            "name": self.name,
            # Allow empty SKU if default_code is not set
            "sku": self.default_code or "",
            "trackInventory": True,
        }

        # Enrich payload via helpers
        self._variant_add_channels(payload)
        self._variant_add_cost_price(payload)
        self._variant_add_channel_listings(payload)
        self._variant_add_weight(payload)

        return payload

    def _saleor_sync_variant(self, saleor_account, product_id):
        """Sync this product variant to Saleor."""
        self.ensure_one()

        if not self.default_code:
            _logger.warning(
                "Skipping variant sync: Missing default_code for product variant ID %s",
                self.id,
            )
            return None

        client = saleor_account._get_client()

        try:
            if self.saleor_variant_id:
                # Update existing variant
                saleor_account._refresh_token(client)
                payload = self._saleor_prepare_variant_payload(product_id)
                result = client.product_variant_update(self.saleor_variant_id, payload)
            else:
                # Create new variant
                saleor_account._refresh_token(client)
                result = client.product_variant_create(
                    product_id=product_id,
                    # Allow empty SKU if default_code is not set
                    sku=self.default_code or "",
                    name=self.name,
                    attributes=[],
                    weight=(
                        float(self.weight) if self.weight and self.weight > 0 else None
                    ),
                )

                # Save the Saleor variant ID and post success message
                if result and result.get("id"):
                    self.sudo().write({"saleor_variant_id": result["id"]})
                    # Use the existing _post_success method from saleor.account
                    saleor_account._post_success(
                        rec=self,
                        object_type="product_variant",
                        slug=self.default_code or str(self.id),
                        payload={
                            "name": self.name,
                            "sku": self.default_code or str(self.id),
                        },
                        saleor_id=result["id"],
                    )

                    # If variant/template has channels, update variant channels now
                    preferred = self.channel_ids or self.product_tmpl_id.channel_ids
                    channel_saleor_ids = [
                        ch.saleor_channel_id for ch in preferred if ch.saleor_channel_id
                    ]
                    if channel_saleor_ids:
                        try:
                            saleor_account._refresh_token(client)
                            # Build per-channel listing updates with price and costPrice
                            update_channels = []
                            for ch in preferred:
                                if not ch.saleor_channel_id:
                                    continue
                                entry = {
                                    "channelId": ch.saleor_channel_id,
                                    # Saleor expects PositiveDecimal (string)
                                    "price": str(float(self.lst_price or 0.0)),
                                }
                                try:
                                    tmpl_currency = (
                                        self.product_tmpl_id.currency_id.name
                                    )
                                    if (
                                        tmpl_currency
                                        and self.standard_price is not None
                                    ):
                                        # PositiveDecimal (string)
                                        entry["costPrice"] = str(
                                            float(self.standard_price)
                                        )
                                except Exception as e:
                                    _logger.debug(
                                        "Saleor: skip per-channel costPrice for %s: %s",
                                        self.display_name,
                                        e,
                                    )
                                update_channels.append(entry)

                            if update_channels:
                                client.product_variant_channel_listing_update(
                                    result["id"], update_channels
                                )
                        except Exception as e:
                            _logger.warning(
                                "Failed to set channels for variant %s"
                                " after create: %s",
                                self.default_code or self.id,
                                str(e),
                            )

            return result

        except Exception as e:
            _logger.error(
                "Failed to sync variant %s to Saleor: %s",
                self.default_code or self.id,
                str(e),
            )
            raise UserError(_("Failed to sync variant to Saleor: %s", str(e))) from e

    def action_saleor_sync(self):
        """Action to sync product variants to all active Saleor accounts.

        This method can be called from the UI to sync one or multiple variants.
        """
        # Ensure inventory sync is enabled before allowing Saleor sync on variants
        invalid = self.filtered(lambda variant: not variant.sync_to_saleor)
        if invalid:
            names = "\n- " + "\n- ".join(invalid.mapped("display_name"))
            raise UserError(
                _(
                    "Please enable 'Sync Variant to Saleor' on the following "
                    "variants before running Saleor synchronization:%s",
                    names,
                )
            )

        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            variant = self
            product_tmpl = variant.product_tmpl_id
            if not product_tmpl.saleor_product_id:
                raise UserError(
                    _(
                        "Parent product %s is not synced with Saleor yet."
                        " Please sync the product first.",
                        product_tmpl.name,
                    )
                )
            payload = variant._saleor_prepare_variant_payload(
                product_tmpl.saleor_product_id
            )
            account.job_product_variant_sync(
                variant.id, product_tmpl.saleor_product_id, payload
            )
        else:
            # Batch multi variants
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for variant in self:
                product_tmpl = variant.product_tmpl_id
                if not product_tmpl.saleor_product_id:
                    raise UserError(
                        _(
                            "Parent product %s is not synced with Saleor yet."
                            " Please sync the product first.",
                            product_tmpl.name,
                        )
                    )
                payload = variant._saleor_prepare_variant_payload(
                    product_tmpl.saleor_product_id
                )
                items.append(
                    {
                        "variant_id": variant.id,
                        "product_saleor_id": product_tmpl.saleor_product_id,
                        "payload": payload,
                    }
                )
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_product_variant_sync_batch(chunk)
                else:
                    account.job_product_variant_sync_batch(chunk)
        return True

    def _notify_saleor_sync(self, warehouse, success=True, error_msg=None):
        """Post chatter notification for Saleor stock sync"""
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

    def action_sync_product_quantities(self):
        """Sync this product's stock quantities to all Saleor warehouses/locations."""
        # Only allow manual quantity sync when inventory sync is enabled
        invalid = self.filtered(lambda product: not product.sync_to_saleor)
        if invalid:
            names = "\n- " + "\n- ".join(invalid.mapped("display_name"))
            raise UserError(
                _(
                    "Please enable 'Sync Variant to Saleor' on the following "
                    "variants before synchronizing quantities to Saleor:%s",
                    names,
                )
            )

        account = get_active_saleor_account(self.env, raise_if_missing=True)

        for product in self:
            if not product.saleor_variant_id:
                product._notify_saleor_sync(
                    success=False, error_msg=_("Missing Saleor Variant ID")
                )
                continue

            # Collect all Saleor-enabled warehouses and locations
            saleor_sources = []
            warehouses = self.env["stock.warehouse"].search(
                [
                    ("is_saleor_warehouse", "=", True),
                    ("include_in_saleor_inventory", "=", True),
                ]
            )
            locations = self.env["stock.location"].search(
                [
                    ("is_saleor_warehouse", "=", True),
                    ("include_in_saleor_inventory", "=", True),
                ]
            )

            for wh in warehouses:
                saleor_sources.append(
                    ("warehouse", wh, wh.view_location_id.id, wh.saleor_warehouse_id)
                )
            for loc in locations:
                saleor_sources.append(
                    ("location", loc, loc.id, loc.saleor_warehouse_id)
                )

            if not saleor_sources:
                raise UserError(_("No Saleor warehouses or locations configured."))

            for _source_type, source_rec, location_id, saleor_wh_id in saleor_sources:
                if not saleor_wh_id:
                    continue

                # Aggregate stock at this location/warehouse
                qty = (
                    self.env["stock.quant"].read_group(
                        domain=[
                            ("product_id", "=", product.id),
                            ("location_id", "child_of", location_id),
                        ],
                        fields=["quantity:sum"],
                        groupby=[],
                    )[0]["quantity"]
                    or 0.0
                )

                try:
                    _logger.info(
                        "Syncing product %s (variant=%s) qty=%s to Saleor warehouse %s",
                        product.display_name,
                        product.saleor_variant_id,
                        qty,
                        source_rec.display_name,
                    )
                    account.with_delay().job_variant_stock_update(
                        variant_id=product.saleor_variant_id,
                        warehouse_id=saleor_wh_id,
                        quantity=qty,
                    )
                    product._notify_saleor_sync(success=True, warehouse=source_rec)
                except Exception as e:
                    _logger.exception(
                        "Failed to sync product %s to Saleor warehouse %s",
                        product.display_name,
                        source_rec.display_name,
                    )
                    product._notify_saleor_sync(
                        success=False, error_msg=str(e), warehouse=source_rec
                    )
