# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import HttpCase


class TestUi(HttpCase):

    def test_price_tiers(self):
        self.phantom_js(
            url_path='/',
            code='odoo.__DEBUG__.services["web_tour.tour"]'
                 '.run("website_sale_price_tier")',
            ready='odoo.__DEBUG__.services["web_tour.tour"]'
                  '.tours.website_sale_price_tier.ready',
        )
