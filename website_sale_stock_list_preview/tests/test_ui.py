# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        product1 = self.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": True,
                "show_availability": True,
                "available_threshold": 99999,
            }
        )
        product2 = self.env["product.template"].create(
            {
                "name": "Test Product 2",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": False,
                "show_availability": True,
            }
        )
        product3 = self.env["product.template"].create(
            {
                "name": "Test Product 3",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": False,
                "show_availability": True,
                "available_threshold": 5,
            }
        )
        self.env["product.template"].create(
            {
                "name": "Test Product 4",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "out_of_stock_message": "test message",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Test Product 5",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Test Product 6",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": True,
                "show_availability": True,
                "out_of_stock_message": "Out of stock",
            }
        )
        self.env["product.template"].create(
            {
                "name": "Test Product 7",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": False,
                "show_availability": True,
            }
        )
        self.env["stock.quant"].create(
            [
                {
                    "product_id": product1.product_variant_id.id,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "quantity": 30.0,
                },
                {
                    "product_id": product2.product_variant_id.id,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "quantity": 30.0,
                },
                {
                    "product_id": product3.product_variant_id.id,
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "quantity": 5.0,
                },
            ]
        )
        self.env.ref("website_sale.products_add_to_cart").active = True
        # Ensure website lang is en_US.
        website = self.env["website"].get_current_website()
        wiz = self.env["base.language.install"].create({"lang": "en_US"})
        wiz.website_ids = website
        wiz.lang_install()
        website.default_lang_id = self.env.ref("base.lang_en")

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_stock_list_preview",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )
