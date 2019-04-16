# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def setUp(self):
        """Ensure website lang is en_US."""
        super().setUp()
        website = self.env["website"].get_current_website()
        wiz = self.env["base.language.install"].create({
            "lang": "en_US",
        })
        wiz.website_ids = website
        wiz.lang_install()
        website.default_lang_id = self.env.ref("base.lang_en")

    def test_ui_website(self):
        """Test frontend tour."""
        tour = "website_sale_require_legal"
        self.browser_js(
            url_path="/shop",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.%s.ready" % tour,
        )
