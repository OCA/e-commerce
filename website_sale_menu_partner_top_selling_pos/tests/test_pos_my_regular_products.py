# Copyright 2026 Daniel Reis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class TestPosMyRegularProducts(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env.ref("website_sale.products_categories").active = True
        cls.partner = cls.env.ref("base.user_admin").partner_id
        cls.product = cls.env["product.product"].create(
            {"name": "POS Product", "list_price": 10.0}
        )
        cls.product.product_tmpl_id.website_published = True
        cls.pos_config = cls.env["pos.config"].create({"name": "Test POS"})
        cls.pos_session = cls.env["pos.session"].create(
            {
                "config_id": cls.pos_config.id,
                "user_id": cls.env.uid,
                "state": "opened",
            }
        )

    def _create_pos_order(self, qty, is_refund=False):
        return self.env["pos.order"].create(
            {
                "session_id": self.pos_session.id,
                "partner_id": self.partner.id,
                "company_id": self.env.company.id,
                "state": "paid",
                "is_refund": is_refund,
                "amount_tax": 0.0,
                "amount_total": qty * self.product.list_price,
                "amount_paid": qty * self.product.list_price,
                "amount_return": 0.0,
                "lines": [
                    Command.create(
                        {
                            "name": "1",
                            "product_id": self.product.id,
                            "qty": qty,
                            "price_unit": self.product.list_price,
                            "price_subtotal": qty * self.product.list_price,
                            "price_subtotal_incl": qty * self.product.list_price,
                        }
                    )
                ],
            }
        )

    def _get_regular_products_page(self):
        self.authenticate("admin", "admin")
        return self.url_open("/shop/my_regular_products")

    def test_pos_purchases_are_listed(self):
        """As a customer, I see the products I bought at the Point of
        Sale on my regular products page."""
        self._create_pos_order(5)

        response = self._get_regular_products_page()
        self.assertEqual(response.status_code, 200)
        self.assertIn("POS Product", response.text)

    def test_pos_refunds_are_deducted(self):
        """As a customer, products fully refunded at the Point of Sale no
        longer appear on my regular products page."""
        self._create_pos_order(5)
        self._create_pos_order(-5, is_refund=True)

        response = self._get_regular_products_page()
        self.assertNotIn("POS Product", response.text)
