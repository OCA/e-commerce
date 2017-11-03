# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp.tests import HttpCase


class TestJS(HttpCase):

    def test_js_tour(self):
        self.phantom_js(
            url_path='/',
            code='odoo.__DEBUG__.services["web.Tour"]'
                 '.run("test_website_sale_qty", "test")',
            ready='odoo.__DEBUG__.services["web.Tour"]'
                  '.tours.test_website_sale_qty',
        )
