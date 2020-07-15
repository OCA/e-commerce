# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class WebsiteSaleTaxesToggleHttpCase(HttpCase):

    def setUp(self):
        super().setUp()
        self.tax = self.env['account.tax'].create({
            'name': 'Taxes tobble test tax',
            'amount_type': 'percent',
            'amount': 15,
            'type_tax_use': 'sale',
        })
        self.product_template = self.env['product.template'].create({
            'name': 'Product test tax toggle',
            'list_price': 750.00,
            'taxes_id': [(6, 0, self.tax.ids)],
            'website_published': True,
            'website_sequence': 9999,
        })
        pricelist = self.env['product.pricelist'].create({
            'name': 'Price list for tests'
        })
        self.env.user.partner_id.property_product_pricelist = pricelist
        # To avoid currency converter
        self.env['res.currency.rate'].search([]).write({
            'rate': 1,
        })

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
