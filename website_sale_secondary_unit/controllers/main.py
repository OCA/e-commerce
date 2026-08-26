# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.cart import Cart
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleSecondaryUnit(WebsiteSale):
    def _prepare_product_values(self, product, category, **kwargs):
        res = super()._prepare_product_values(product, category, **kwargs)
        res["secondary_uom_ids"] = product._get_website_secondary_uoms()
        return res


class CartSecondaryUnit(Cart):
    @http.route()
    def update_cart(self, line_id, quantity, product_id=None, **kwargs):
        """Translate the quantity typed by the customer into product units.

        The cart quantity widget shows secondary units for the lines sold in
        such units (see ``_get_displayed_quantity``), so the received quantity
        has to be converted before hitting the standard cart logic, and the
        returned one converted back.
        """
        order_sudo = request.cart
        line = order_sudo.order_line.filtered(lambda sol: sol.id == line_id)[:1]
        if not line and product_id:
            line = order_sudo.order_line.filtered(
                lambda sol: sol.product_id.id == product_id
            )[:1]
        secondary_uom = line.secondary_uom_id
        if secondary_uom:
            qty_base = float(quantity) * secondary_uom.factor
            quantity = line.product_id.uom_id._compute_quantity(
                qty_base, line.product_uom_id
            )
        values = super().update_cart(
            line_id=line_id, quantity=quantity, product_id=product_id, **kwargs
        )
        if secondary_uom and line.exists():
            values["quantity"] = line._get_displayed_quantity()
        return values

    def _get_cart_notification_information(self, order, added_qty_per_line):
        res = super()._get_cart_notification_information(order, added_qty_per_line)
        for line_values in res.get("lines", []):
            line = order.order_line.browse(line_values["id"])
            if not line.secondary_uom_id:
                continue
            secondary_qty = line._convert_qty_to_secondary_uom(line_values["quantity"])
            line_values["quantity"] = (
                int(secondary_qty)
                if int(secondary_qty) == secondary_qty
                else secondary_qty
            )
        return res

    def _get_additional_cart_notification_information(self, line):
        res = super()._get_additional_cart_notification_information(line)
        if line.secondary_uom_id:
            res["uom_name"] = line.secondary_uom_id._get_website_display_name()
        return res


class ProductConfiguratorSecondaryUnit(WebsiteSaleProductConfiguratorController):
    def _get_product_information(
        self, product_template, combination, currency, pricelist, so_date, **kwargs
    ):
        """Let the customer pick a secondary unit in the product configurator."""
        values = super()._get_product_information(
            product_template, combination, currency, pricelist, so_date, **kwargs
        )
        if not request.is_frontend:
            return values
        secondary_uoms = product_template._get_website_secondary_uoms()
        if not secondary_uoms:
            return values
        default_secondary_uom = product_template.sale_secondary_uom_id & secondary_uoms
        if not default_secondary_uom and not product_template.allow_uom_sell:
            default_secondary_uom = secondary_uoms[:1]
        values.update(
            allow_uom_sell=product_template.allow_uom_sell,
            default_secondary_uom_id=default_secondary_uom.id,
            secondary_uom_id=int(kwargs.get("secondary_uom_id") or 0),
            secondary_uoms=[
                {
                    "id": secondary_uom.id,
                    "display_name": secondary_uom._get_website_display_name(),
                    "factor": secondary_uom.factor,
                }
                for secondary_uom in secondary_uoms
            ],
        )
        return values

    def _get_basic_product_information(
        self,
        product_or_template,
        pricelist,
        combination,
        secondary_uom_id=None,
        **kwargs,
    ):
        """Return the prices of one secondary unit when the customer picks one.

        The configurator multiplies the price by the quantity, which is given in
        the selected unit, just like the standard unit of measure selector does.
        """
        secondary_uom_id = int(secondary_uom_id or 0)
        secondary_uom = request.env["product.secondary.unit"].browse(
            secondary_uom_id or []
        )
        if secondary_uom:
            kwargs["quantity"] = kwargs.get("quantity", 0.0) * secondary_uom.factor
        values = super()._get_basic_product_information(
            product_or_template, pricelist, combination, **kwargs
        )
        if secondary_uom:
            for price_field in ("price", "strikethrough_price"):
                if values.get(price_field):
                    values[price_field] *= secondary_uom.factor
        return values
