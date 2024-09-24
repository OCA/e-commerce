#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class TestUi(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "website_published": True,
            }
        )
        cls.env.ref("website_sale_cart_clear.cart_lines").active = True

    def test_tour(self):
        self.start_tour(
            "/shop",
            "website_sale_cart_clear_tour",
        )
