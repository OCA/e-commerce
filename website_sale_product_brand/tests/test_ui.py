# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):

    def test_ui_website(self):
        """Test frontend tour."""
        tour = "website_sale_product_brand"
        self.phantom_js(
            url_path="/shop",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('%s')" % tour,
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.%s.ready" % tour)
