# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(
            search, category, attrib_values
        )
        for i, v in enumerate(domain):
            if not isinstance(v, tuple):
                continue

            if not len(v) == 3:
                continue

            if v[0] == 'name' and v[1] == 'ilike':
                domain[i] = (v[0], '%', v[2])

        return domain
