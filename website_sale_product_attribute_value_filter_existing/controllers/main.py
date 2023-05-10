# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import http
from odoo.http import request
from odoo.tools import lazy

from odoo.addons.website_sale.controllers.main import WebsiteSale


class ProductAttributeValues(WebsiteSale):
    @http.route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post
    ):
        res = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )

        # getting existing templates by "search_product" in qcontext
        # without searching again
        templates = res.qcontext["search_product"]
        ProductTemplateAttributeLine = request.env["product.template.attribute.line"]
        attribute_values = lazy(
            lambda: ProductTemplateAttributeLine.search(
                [("product_tmpl_id", "in", templates.ids)]
            )
        )
        res.qcontext["attr_values_used"] = attribute_values.mapped("value_ids")
        return res
