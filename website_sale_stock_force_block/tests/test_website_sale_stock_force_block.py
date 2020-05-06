# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class websiteSaleStockForceBlock(HttpCase):

    def setUp(self):
        super().setUp()
        # Active "Add to cart" option in main products view
        self.env.ref('website_sale.products_add_to_cart').active = True

        # For testing with website_sale_vat_required module, I avoid
        # address step to fill partner vat
        self.env.ref('base.user_admin').partner_id.write({
            'vat': 'BE0477472701',
            'phone': '9999999999',
        })
        self.ProductTemplate = self.env['product.template']
        # The website_sequence is set quite high to display this products in
        # first page.
        # Set list price to 0.0 to avoid payment step because this step has an
        # asynchronous call
        common_vals = {
            'type': 'product',
            'website_published': True,
            'inventory_availability': 'custom_block',
            'website_sequence': 5000,
            'list_price': 0.0,
        }
        vals = common_vals.copy()
        vals.update({
            'name': 'Computer Motherboard',
            'custom_message': 'Temporarily not available',
        })
        self.product_template = self.ProductTemplate.create(vals)

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_stock_force_block",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
