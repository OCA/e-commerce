# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):
    def checkout_values(self, data=None):
        result = super(WebsiteSale, self).checkout_values(data)
        if result and data:
                result['checkout']['note'] = data.get('note', False)
        return result

    def checkout_form_save(self, checkout):
        res = super(WebsiteSale, self).checkout_form_save(checkout)
        if 'note' in checkout:
            order = request.website.sale_get_order(
                force_create=1, context=request.context)
            order.note = checkout['note']
        return res
