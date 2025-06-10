# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import http
from odoo.http import request
from odoo.modules import get_module_path


class StarRatingXMLController(http.Controller):
    @http.route(
        "/shop/website_sale_product_review/<path:file>",
        type="http",
        auth="public",
        website=True,
    )
    def star_rating_xml(self, file, **kwargs):
        module_path = get_module_path("website_sale_product_review")
        file_path = os.path.join(module_path, file)
        if not os.path.exists(file_path):
            return request.not_found()
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return request.make_response(
            content,
            headers=[("Content-Type", "text/xml")],
        )
