# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class websiteSaleStockAvailableDisplay(HttpCase):

    def setUp(self):
        super().setUp()
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
            'inventory_availability': 'always_no_lock',
            'website_sequence': 5000,
            'list_price': 0.0,
        }
        vals = common_vals.copy()
        vals.update({
            'name': 'Computer Motherboard',
            'custom_message': 'Available in 10 days',
        })
        self.product_template_wo_qty = self.ProductTemplate.create(vals)
        vals = common_vals.copy()
        vals.update({
            'name': 'Special Mouse',
        })
        self.product_product_w_qty = self.ProductTemplate.create(vals)
        self.env['stock.quant'].create({
            'product_id': self.product_product_w_qty.product_variant_ids.id,
            'product_uom_id': self.product_product_w_qty.uom_id.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'quantity': 10.0,
        })

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_stock_available_display",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
