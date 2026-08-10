# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleProductDetailAttributeImage(WebsiteSale):
    @http.route()
    def product(self, product, category=None, pricelist=None, **kwargs):
        res = super().product(product, category=category, pricelist=pricelist, **kwargs)
        attributes_detail = product.attribute_line_ids.filtered(
            lambda x: x.attribute_id.website_product_detail_image_published
        )
        res.qcontext["attributes_detail"] = attributes_detail
        return res
