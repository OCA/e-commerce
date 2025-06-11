# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import http
from odoo.http import request
from odoo.modules import get_module_path


class StarRatingXMLController(http.Controller):
    @http.route(
        "/shop/product_review/portal/<path:file>",
        type="http",
        auth="user",
        website=True,
    )
    def star_rating_xml(self, file, **kwargs):
        content = "<div></div>"
        module_path = get_module_path("website_sale_product_review")
        file_path = os.path.join(module_path, file)
        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        return request.make_response(
            content,
            headers=[("Content-Type", "text/xml")],
        )

    @http.route(
        '/shop/product_review/<model("product.template"):product_template>/post_review',
        type="json",
        auth="user",
        website=True,
    )
    def post_review(self, product_template, access_token=None, **post):
        if product_template and access_token:
            pass
        return {"error": False}
