# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def test_ui_website(self):
        """Test frontend tour."""
        self.phantom_js(
            url_path="/",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('test_website_sale_wishlist', 'test')",
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.test_website_sale_wishlist.ready")
