# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests import HttpCase


class TestJS(HttpCase):

    def test_js_tour(self):
        tour = "odoo.__DEBUG__.services['web_tour.tour']"
        self.phantom_js(
            "/",
            "%s.run('test_website_sale_price_subtotal')" % tour,
            "%s.tours.test_website_sale_price_subtotal.ready" % tour,
            login="admin",
        )
