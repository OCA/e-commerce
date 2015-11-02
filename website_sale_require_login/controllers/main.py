# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import http
from openerp.addons.website_sale.controllers.main import website_sale


class RequireLoginToCheckout(website_sale):
    @http.route(auth="user")
    def checkout(self, **post):
        return super(RequireLoginToCheckout, self).checkout(**post)
