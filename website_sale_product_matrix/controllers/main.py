# Copyright 2025 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleProductMatrix(WebsiteSale):
    @route(
        ["/shop/cart/update_from_matrix"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def cart_update_from_matrix(self, product_template_id, grid, **kw):
        """This route is called when adding a product to cart from the product matrix"""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != "draft":
            request.session["sale_order_id"] = None
            sale_order = request.website.sale_get_order(force_create=True)
        sale_order.update(
            {
                "grid_product_tmpl_id": int(product_template_id),
                "grid_update": True,
                "grid": grid,
            }
        )
        sale_order._apply_grid()
        return request.redirect("/shop/cart")
