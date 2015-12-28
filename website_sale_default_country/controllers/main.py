# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):
    def checkout_values(self, data=None):
        result = super(WebsiteSale, self).checkout_values(data)
        try:
            result["checkout"].setdefault(
                "country_id",
                request.website.company_id.country_id.id)
        except KeyError:
            pass
        return result
