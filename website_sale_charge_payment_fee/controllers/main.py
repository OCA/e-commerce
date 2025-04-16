# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFee(WebsiteSale):
    @http.route(
        "/shop/payment/get_fee",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_payment_fee(self, provider_id=None, **kw):
        order = request.website.sale_get_order()
        Monetary = request.env["ir.qweb.field.monetary"]

        if not provider_id or not order:
            return {
                "amount_payment_fee": Monetary.value_to_html(
                    0.0, {"display_currency": order.currency_id}
                )
            }

        provider = request.env["payment.provider"].browse(int(provider_id))
        price = order._calculate_payment_fee_price(provider)
        line_id = order.update_fee_line(provider)
        return {
            "amount_payment_fee": Monetary.value_to_html(
                price, {"display_currency": order.currency_id}
            ),
            "line_id": line_id.id,
            "product_id": line_id.product_id.id,
        }

    def _remove_payment_fee(self):
        order = request.website.sale_get_order()
        if order and order.order_line:
            fee_lines = order.order_line.filtered(lambda line: line.payment_fee_line)
            if fee_lines:
                fee_lines.unlink()

    @http.route(
        [
            "/shop",
            "/shop/page/<int:page>",
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=WebsiteSale.sitemap_shop,
    )
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post,
    ):
        self._remove_payment_fee()
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post,
        )

    @http.route(
        ['/shop/product/<model("product.template"):product>'],
        type="http",
        auth="public",
        website=True,
    )
    def old_product(self, product, category="", search="", **kwargs):
        self._remove_payment_fee()
        return super().old_product(product, category=category, search=search, **kwargs)

    @http.route(["/shop/cart"], type="http", auth="public", website=True)
    def cart(self, access_token=None, revive="", **post):
        self._remove_payment_fee()
        return super().cart(access_token=access_token, revive=revive, **post)

    @http.route(
        ['/shop/<model("product.template"):product>'],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def product(self, product, category="", search="", **kwargs):
        return super().product(product, category=category, search=search, **kwargs)
