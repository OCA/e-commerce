# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product1 = cls.env["product.template"].create(
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
        product2 = cls.env["product.template"].create(
            {
                "name": "Test Product 2",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": False,
                "show_availability": True,
            }
        )
        product3 = cls.env["product.template"].create(
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
        cls.env["product.template"].create(
            {
                "name": "Test Product 4",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "out_of_stock_message": "test message",
            }
        )
        cls.env["product.template"].create(
            {
                "name": "Test Product 5",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
            }
        )
        cls.env["product.template"].create(
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
        cls.env["product.template"].create(
            {
                "name": "Test Product 7",
                "is_published": True,
                "website_sequence": 1,
                "type": "product",
                "allow_out_of_stock_order": False,
                "show_availability": True,
            }
        )
        cls.env["stock.quant"].create(
            [
                {
                    "product_id": product1.product_variant_id.id,
                    "location_id": cls.env.ref("stock.stock_location_stock").id,
                    "quantity": 30.0,
                },
                {
                    "product_id": product2.product_variant_id.id,
                    "location_id": cls.env.ref("stock.stock_location_stock").id,
                    "quantity": 30.0,
                },
                {
                    "product_id": product3.product_variant_id.id,
                    "location_id": cls.env.ref("stock.stock_location_stock").id,
                    "quantity": 5.0,
                },
            ]
        )
        cls.env.ref("website_sale.products_add_to_cart").active = True
        # Ensure website lang is en_US.
        website = cls.env["website"].get_current_website()
        en_us = (
            cls.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "en_US")])
        )
        wiz = cls.env["base.language.install"].create({"lang_ids": en_us.ids})
        wiz.website_ids = website
        wiz.lang_install()
        website.default_lang_id = cls.env.ref("base.lang_en")

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_stock_list_preview",
            login="admin",
        )
