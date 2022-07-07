# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleTierValidation(WebsiteSale):
    @route()
    def confirm_order(self, **post):
        order = request.website.sale_get_order()
        if order.need_validation or order.review_ids:
            return request.redirect("/shop/validation")
        return super().confirm_order(**post)

    @route()
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            assert order.id == request.session.get("sale_last_order_id")
        if order.need_validation or order.review_ids:
            order.with_context(send_email_customer=True).request_validation()
            request.website.sale_reset()
            return request.redirect("/shop")
        return super().payment_validate(
            transaction_id=transaction_id, sale_order_id=sale_order_id, **post
        )

    @route(
        ["/shop/validation"], type="http", auth="public", website=True, sitemap=False
    )
    def validation_page(self, **post):
        order = request.website.sale_get_order()
        render_values = self._get_shop_payment_values(order, **post)
        return request.render(
            "website_sale_tier_validation.validation_page", render_values
        )
