# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json as _json
import logging

from odoo import Command, api, fields, models
from odoo.exceptions import UserError

from ..helpers import html_to_editorjs

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[
            ("saleor", "Saleor Delivery"),
        ],
        ondelete={"saleor": "cascade"},
    )
    shipping_method_type = fields.Selection(
        selection=[
            ("price", "Price"),
            ("weight", "Weight"),
        ],
        required=True,
        default="price",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=False,
        ondelete="cascade",
    )
    tax_id = fields.Many2one(
        "account.tax",
        domain=[("type_tax_use", "=", "sale")],
    )
    saleor_shipping_method_id = fields.Char(
        string="Saleor Shipping Method ID", copy=False, index=True
    )
    zone_id = fields.Many2one("saleor.shipping.zone", string="Shipping Zone")
    zone_channel_ids = fields.Many2many(
        "saleor.channel", string="Channels", related="zone_id.channel_ids"
    )
    description = fields.Html()
    min_delivery_time = fields.Float()
    max_delivery_time = fields.Float()
    order_value = fields.Boolean(
        help="Restrict order value.\nThis rate will apply to all orders",
    )
    saleor_order_value_line_ids = fields.One2many(
        "order.value.line",
        "carrier_id",
    )
    saleor_shipping_pricing_line_ids = fields.One2many(
        "shipping.pricing.line",
        "carrier_id",
        string="Pricing",
    )
    # Postal codes
    postal_filter_mode = fields.Selection(
        selection=[
            ("exclude", "Exclude postal codes"),
            ("include", "Include postal codes"),
        ],
        default="exclude",
        required=True,
        string="Postal Codes Mode",
    )
    postal_code_range_ids = fields.One2many(
        "postal.code.range", "carrier_id", string="Postal Code Ranges"
    )
    excluded_product_ids = fields.Many2many(
        "product.template",
        string="Excluded Products",
    )
    # Metadata for Price Based Rates
    shipping_method_metadata_line_ids = fields.One2many(
        "shipping.method.meta.line", "carrier_id", string="Metadata"
    )
    shipping_method_private_metadata_line_ids = fields.One2many(
        "shipping.method.private.meta.line", "carrier_id", string="Private Metadata"
    )

    @api.onchange("postal_filter_mode")
    def _onchange_postal_filter_mode(self):
        for rec in self:
            rec.postal_code_range_ids = [Command.clear()]

    @api.model_create_multi
    def create(self, vals_list):
        carriers = super().create(vals_list)
        ProductTemplate = self.env["product.template"]

        for carrier in carriers:
            if carrier.delivery_type == "saleor" and not carrier.product_id:
                product_tmpl = ProductTemplate.create(
                    {
                        "name": carrier.name,
                        "type": "service",
                        "sale_ok": False,
                        "purchase_ok": False,
                        "list_price": 0.0,
                        "taxes_id": [Command.clear()],
                        "invoice_policy": "order",
                    }
                )
                carrier.product_id = product_tmpl.product_variant_id.id
                # If carrier has a tax set, add it to the created product's taxes
                if carrier.tax_id:
                    product_tmpl.write({"taxes_id": [Command.link(carrier.tax_id.id)]})

        # Ensure any existing product linked to a Saleor carrier also receives its tax
        for carrier in carriers:
            if (
                carrier.delivery_type == "saleor"
                and carrier.product_id
                and carrier.tax_id
            ):
                carrier.product_id.product_tmpl_id.write(
                    {"taxes_id": [Command.link(carrier.tax_id.id)]}
                )

        return carriers

    def write(self, vals):
        res = super().write(vals)
        # When tax or product changes on a Saleor carrier, add tax to the product
        if any(k in vals for k in ("tax_id", "product_id", "delivery_type")):
            for carrier in self:
                try:
                    if (
                        carrier.delivery_type == "saleor"
                        and carrier.product_id
                        and carrier.tax_id
                    ):
                        carrier.product_id.product_tmpl_id.write(
                            {"taxes_id": [Command.link(carrier.tax_id.id)]}
                        )
                except Exception:
                    # Do not block writes for ancillary errors
                    _logger.debug("Skipping tax propagation for carrier %s", carrier.id)
        return res

    def saleor_rate_shipment(self, order):
        """Compute shipping price for Saleor delivery methods.

        This mirrors the logic used in the choose.delivery.carrier wizard
        for delivery_type == "saleor", so that any caller of
        delivery.carrier.rate_shipment() (website, recompute, etc.)
        behaves consistently.
        """
        self.ensure_one()

        sale_order = order
        saleor_channel = sale_order.saleor_channel_id

        # Persist chosen carrier on the order for later Saleor sync jobs
        try:
            sale_order.saleor_delivery_carrier_id = self.id
        except Exception:
            _logger.debug(
                "Could not set saleor_delivery_carrier_id on sale.order %s",
                sale_order.id,
            )

        if not saleor_channel:
            raise UserError(
                self.env._("This order does not have a Saleor channel linked.")
            )

        price_line = self.saleor_shipping_pricing_line_ids.filtered(
            lambda line, ch=saleor_channel: line.channel_id == ch
        )

        if not price_line:
            raise UserError(
                self.env._(
                    "No shipping price configured for channel '%s'.",
                    saleor_channel.name,
                )
            )

        price = price_line[0].price

        return {
            "success": True,
            "price": price,
            "error_message": False,
            "warning_message": False,
        }

    def saleor_send_shipping(self, pickings):
        """Dummy shipment handler for Saleor carriers.

        Core stock_delivery expects send_shipping() to return a list of dicts
        with at least keys 'exact_price' and 'tracking_number'. For Saleor
        delivery methods, the actual fulfillment and tracking are managed on
        the Saleor side via sync jobs, so here we just return a minimal
        structure to avoid errors in stock_picking.send_to_shipper.

        :param pickings: stock.picking recordset (ignored here)
        :return: list[dict] in the format expected by stock_delivery
        """
        self.ensure_one()

        return [
            {
                "exact_price": 0.0,
                "tracking_number": False,
            }
        ]

    def _saleor_shipping_method_prepare_payload(self):
        """Build payload for Saleor shipping method create/update."""
        self.ensure_one()
        payload = {
            "name": self.name,
        }

        # Type mapping
        if self.shipping_method_type == "price":
            payload["type"] = "PRICE"
        elif self.shipping_method_type == "weight":
            payload["type"] = "WEIGHT"

        # Description: convert HTML to EditorJS JSON string
        if self.description:
            desc = html_to_editorjs(self.description)
            if desc is not None:
                payload["description"] = _json.dumps(desc)

        # Delivery time (days) - always include (0 if not set)
        payload["minimumDeliveryDays"] = int(self.min_delivery_time or 0)
        payload["maximumDeliveryDays"] = int(self.max_delivery_time or 0)

        # Weight constraints for weight-based shipping methods
        if self.shipping_method_type == "weight":
            # Get weight constraints from order value lines
            if self.saleor_order_value_line_ids:
                # Use the first order value line for weight constraints
                # In weight-based methods, min_value/max_value represent weight limits
                weight_line = self.saleor_order_value_line_ids[0]
                if weight_line.min_value:
                    payload["minimumOrderWeight"] = float(weight_line.min_value)
                if weight_line.max_value:
                    payload["maximumOrderWeight"] = float(weight_line.max_value)

        # Postal code rules
        inclusion = "INCLUDE" if self.postal_filter_mode == "include" else "EXCLUDE"
        payload["inclusionType"] = inclusion
        add_rules = [
            {
                "start": (rng.start_zip or ""),
                "end": (rng.end_zip or ""),
            }
            for rng in self.postal_code_range_ids
            if (rng.start_zip or rng.end_zip)
        ]
        if add_rules:
            payload["addPostalCodeRules"] = add_rules

        # Metadata and private metadata
        meta = [
            {"key": line.key, "value": line.value}
            for line in (self.shipping_method_metadata_line_ids or [])
        ]
        priv = [
            {"key": line.key, "value": line.value}
            for line in (self.shipping_method_private_metadata_line_ids or [])
        ]
        if meta:
            payload["metadata"] = meta
        if priv:
            payload["privateMetadata"] = priv

        # Excluded products
        payload["excludedProducts"] = [
            tmpl.saleor_product_id
            for tmpl in self.excluded_product_ids
            if getattr(tmpl, "saleor_product_id", None)
        ]

        # Inject tax class if available on carrier's tax
        try:
            tax_class_id = getattr(
                getattr(self, "tax_id", None), "saleor_tax_class_id", None
            )
            if tax_class_id:
                payload["taxClass"] = tax_class_id
        except Exception as e:
            _logger.warning(
                "Failed to inject taxClass for carrier %s: %s",
                getattr(self, "id", None),
                e,
            )

        return payload
