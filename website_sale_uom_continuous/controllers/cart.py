# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.cart import Cart


class WebsiteSaleUomContinuousCart(Cart):
    @route(type="jsonrpc")
    def add_to_cart(self, product_template_id, product_id, quantity=1.0, **kwargs):
        # OVERRIDE: keep the decimals of the added quantity.
        # Core casts the quantity to an integer before adding it to the cart:
        # https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/controllers/cart.py#L114
        # The cart gets the requested one through its context instead, keyed by the
        # added product (see ``sale.order._cart_add``).
        order_sudo = request.cart or request.website._create_cart()
        request.cart = order_sudo.with_context(
            website_sale_uom_continuous_add_qty={product_id: float(quantity)}
        )
        return super().add_to_cart(
            product_template_id, product_id, quantity=quantity, **kwargs
        )

    @route(type="jsonrpc")
    def update_cart(self, line_id, quantity, product_id=None, **kwargs):
        # OVERRIDE: keep the decimals of the updated quantity.
        # Core casts the quantity to an integer before updating the cart line:
        # https://github.com/odoo/odoo/blob/b3e4ddcbcc3a6a5a28f18f70342dcd584432faef/addons/website_sale/controllers/cart.py#L329
        # The cart gets the requested one through its context instead, keyed by the
        # updated line (see ``sale.order._cart_update_line_quantity``).
        # Same line lookup as core when no line is given, to key the quantity by it.
        if not line_id and request.cart:
            line_id = request.cart.order_line.filtered(
                lambda sol: sol.product_id.id == product_id
            )[:1].id
        if request.cart:
            request.cart = request.cart.with_context(
                website_sale_uom_continuous_update_qty={line_id: float(quantity)}
            )
        return super().update_cart(line_id, quantity, product_id=product_id, **kwargs)
