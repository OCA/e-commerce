# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        product1 = self.env['product.template'].create({
            'name': 'Test Product 1',
            'is_published': True,
            'virtual_available': 10,
            'website_sequence': 100000,
        })
        product2 = self.env['product.template'].create({
            'name': 'Test Product 2',
            'is_published': True,
            'virtual_available': 0,
            'website_sequence': 100000,
        })

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_show_stock_preview",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )

