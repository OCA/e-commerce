# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import http
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        """ Overload to inject pricelist item ids if necessary. """

        context = http.request.env.context
        domain = super(WebsiteSale, self)._get_search_domain(
            search, category, attrib_values
        )

        if not context.get('pricelist'):
            pricelist_id_int = self.get_pricelist().id
        else:
            pricelist_id_int = context['pricelist']

        domain.extend([
            ('item_ids.pricelist_id', '=', pricelist_id_int),
        ])

        return domain
