# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleReferenceDisplayed(WebsiteSaleVariantController):
    @http.route()
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, **kw
    ):
        res = super().get_combination_info_website(
            product_template_id, product_id, combination, add_qty, **kw
        )
        variant_id = res.get("product_id")
        if variant_id:
            variant = request.env["product.product"].browse(variant_id)
            variant_reference = variant.default_code or None
        else:
            variant_reference = None
        res["variant_reference"] = variant_reference
        return res
