# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale


class RequireLoginToCheckout(WebsiteSale):
    @http.route(['/shop/checkout'], type='http', auth="user", website=True)
    def checkout(self, **post):
        return super(RequireLoginToCheckout, self).checkout(**post)
