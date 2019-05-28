# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http


class WebsiteSaleProductDetailAttributeImage(WebsiteSale):

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        res = super().product(
            product, category=category, search=search, **kwargs)
        attributes_detail = product.attribute_line_ids.filtered(
            lambda x: x.attribute_id.website_product_detail_image_published)
        res.qcontext['attributes_detail'] = attributes_detail
        return res
