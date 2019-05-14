# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_product_attribute_value_filter_existing",
        )
        self.phantom_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
