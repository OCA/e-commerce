# -*- coding: utf-8 -*-
# © 2017 Andrei Poehlmann (andrei.poehlmann90@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def test_ui_website(self):
        """Test frontend tour."""
        self.phantom_js(
            url_path="/",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('test_website_sale_recently_viewed_products', 'test')",
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.test_website_sale_recently_viewed_products.ready")
