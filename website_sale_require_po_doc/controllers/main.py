# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleRequirePoDoc(WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        res = super()._get_shop_payment_values(order, **kwargs)
        if order:
            res["customer_need_po"] = order.partner_id.customer_need_po
            res["client_order_ref"] = order.client_order_ref or ""
        return res

    @route(
        "/shop/set_client_order_ref",
        type="jsonrpc",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def set_client_order_ref(self, client_order_ref=""):
        order = request.cart
        if order:
            order.client_order_ref = client_order_ref
        return
