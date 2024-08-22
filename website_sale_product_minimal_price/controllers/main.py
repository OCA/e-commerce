# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleVariantController(WebsiteSaleVariantController):
    @http.route(
        ["/website_sale/get_combination_info_pricelist_atributes"],
        type="json",
        auth="public",
        website=True,
    )
    def get_combination_info_pricelist_atributes(self, product_id, **kwargs):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        # Copied from _get_combination_info
        # /odoo/addons/website_sale/models/product_template.py
        website = (
            request.env["website"]
            .get_current_website()
            .with_context(**request.env.context)
        )
        pricelist = website.pricelist_id
        product = (
            request.env["product.product"]
            .browse(product_id)
            .with_context(pricelist=pricelist.id)
        )
        # Getting all min_quantity of the current product to compute the possible
        # price scale.
        qty_list = request.env["product.pricelist.item"].search(
            product._get_product_pricelist_item_domain()
        )
        qty_list = sorted(set(qty_list.mapped("min_quantity")))

        return product._get_product_price_scale(qty_list)
