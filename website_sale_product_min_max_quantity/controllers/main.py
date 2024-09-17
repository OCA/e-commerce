# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# Copyright 2024 Binhex - Adasat Torres <a.torres@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class WebsiteSale(http.Controller):
    @http.route(
        ["/shop/cart/update"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product = request.env["product.template"].browse(int(product_id))
        min_qty = product.website_sale_min_qty
        max_qty = product.website_sale_max_qty
        if add_qty < min_qty:
            add_qty = min_qty
        if add_qty > max_qty:
            add_qty = max_qty
        return super().cart_update(product_id, add_qty, set_qty, **kw)

    @http.route(
        ["/shop/cart/update_json"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True
    ):
        product = request.env["product.template"].browse(int(product_id))
        min_qty = product.website_sale_min_qty
        max_qty = product.website_sale_max_qty
        if add_qty < min_qty:
            add_qty = min_qty
        if add_qty > max_qty:
            add_qty = max_qty
        return super().cart_update_json(product_id, line_id, add_qty, set_qty, display)
