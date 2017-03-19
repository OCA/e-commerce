# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import HttpCase


class TestJS(HttpCase):

    post_install = True
    at_install = False

    def test_js_tour(self):
        tour = "odoo.__DEBUG__.services['web_tour.tour']"
        self.phantom_js(
            "/",
            "%s.run('test_website_sale_qty')" % tour,
            "%s.tours.test_website_sale_qty.ready" % tour,
            login="admin",
        )
