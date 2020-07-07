# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleTaxesToggleHttpCase(HttpCase):

    def setUp(self):
        super().setUp()
        # Customizable desk
        self.product_template = self.env.ref(
            'product.product_product_4_product_template')
        self.tax = self.env['account.tax'].create({
            'name': 'Taxes tobble test tax',
            'amount_type': 'percent',
            'amount': 15,
            'type_tax_use': 'sale',
        })
        self.product_template.list_price = 750.00
        self.product_template.taxes_id = [(6, 0, self.tax.ids)]

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_tax_toggle",
        )
        self.browser_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
