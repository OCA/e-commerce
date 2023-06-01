# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp.tests.common import HttpCase


class UICase(HttpCase):
    def setUp(self):
        """Ensure website lang is en_US."""
        super(UICase, self).setUp()
        with self.cursor() as cr:
            env = self.env(cr)
            website = env["website"].get_current_website()
            wiz = env["base.language.install"].create({
                "lang": "en_US",
            })
            wiz.website_ids = website
            wiz.lang_install()
            website.default_lang_id = env.ref("base.lang_en")

    def test_ui_website(self):
        """Test frontend tour."""
        tour = "website_sale_require_legal"
        self.phantom_js(
            url_path="/shop",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.%s.ready" % tour)
