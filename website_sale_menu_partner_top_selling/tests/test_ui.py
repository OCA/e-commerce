# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env.ref("website_sale.products_categories").active = True
        cls.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.limit", 2
        )
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.partner = cls.admin_user.partner_id
        cls.products = []
        for i in range(1, 6):
            product = cls.env["product.product"].create(
                {
                    "name": f"Product {i}",
                    "list_price": 10.0 * i,
                }
            )
            product.product_tmpl_id.website_published = True
            cls.products.append(product)
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        quantities = [50, 30, 70, 10, 90]
        for product, qty in zip(cls.products, quantities, strict=True):
            cls.env["sale.order.line"].create(
                {
                    "order_id": cls.sale_order.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "price_unit": product.list_price,
                }
            )
        cls.sale_order.action_confirm()
        # Unconfirmed order, no products to be counted
        cls.sale_order_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_2.id,
                "product_id": cls.products[0].id,
                "product_uom_qty": 1000,
                "price_unit": cls.products[0].list_price,
            }
        )

    def test_ui(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_menu_partner_top_selling",
            login="admin",
        )

    def test_pagination(self):
        """As a customer, page N of my regular products shows the Nth page of
        products, and an out-of-range page is clamped to the last one."""
        # Two regular products (limit is 2 in setUpClass), one per page.
        website = self.env["website"].search([], limit=1)
        website.shop_ppg = 1
        self.authenticate("admin", "admin")

        # Products are sorted by purchased quantity, descending: the top two
        # are Product 5 (90) and Product 3 (70).
        first_page = self.url_open("/shop/my_regular_products/page/1").text
        self.assertIn("Product 5", first_page)
        self.assertNotIn("Product 3", first_page)

        second_page = self.url_open("/shop/my_regular_products/page/2").text
        self.assertIn("Product 3", second_page)
        self.assertNotIn("Product 5", second_page)

        # There are only two pages: page 99 shows the last one.
        clamped_page = self.url_open("/shop/my_regular_products/page/99").text
        self.assertIn("Product 3", clamped_page)
        self.assertNotIn("Product 5", clamped_page)

    def test_category_query_param_redirects(self):
        """As a customer, the deprecated ``category`` query parameter on my
        regular products redirects to the shop category page instead of
        failing."""
        category = self.env["product.public.category"].create({"name": "Shoes"})
        self.authenticate("admin", "admin")

        response = self.url_open(
            f"/shop/my_regular_products?category={category.id}",
            allow_redirects=False,
        )
        self.assertEqual(response.status_code, 301)
        self.assertIn("/shop/category/", response.headers["Location"])
