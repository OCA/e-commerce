# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.web import http
from openerp.addons.web.http import request


class website_sale(http.Controller):

    @http.route(['/shop/shoping_cart_website_notes'],
                type='json',
                auth="public",
                methods=['POST'],
                website=True)
    def shoping_cart_website_notes(self, **kw):
        request.env['sale.order.line'].sudo() \
            .browse(int(kw.get('line_id')))\
            .write({'website_note': kw.get('website_note')})
        return True
