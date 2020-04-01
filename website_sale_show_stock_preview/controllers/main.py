# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.sale.controllers.variant import VariantController


class WebsiteSaleVariantController(VariantController):
    @http.route(['/sale/get_combination_info_stock_preview'], type='json', auth="public", methods=['POST'], website=True)
    def get_combination_info_stock_preview(self, product_template_ids, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        # return self.get_website_stock_preview(product_template_ids, **kw)

        res = []
        for template in request.env['product.template'].sudo().with_context(website_sale_stock_get_quantity=True).browse(product_template_ids):
            res.append({'id': template.id, 'virtual_available': template.virtual_available})
        return res
