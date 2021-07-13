# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request


class WebsiteSale(http.Controller):
    @http.route(["""/promotions"""], type="http", auth="public", website=True)
    def promotion(self, **post):
        all_promos = (
            request.env["sale.coupon.program"]
            .sudo()
            .search(
                [
                    ("is_published", "=", True),
                    "|",
                    ("website_id", "=", False),
                    ("website_id", "=", request.env.context.get("website_id")),
                ]
            )
        )
        promos = request.env["sale.coupon.program"]
        for promo in all_promos:
            if promo._is_valid_partner(request.env.user.partner_id):
                promos |= promo
        values = {"promos": promos}
        return request.render("website_sale_coupon_page.available_promotions", values)
