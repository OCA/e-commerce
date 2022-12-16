from odoo.tests import SavepointCase, tagged

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_payment_term_acquirer.controllers.main import WebsiteSale


@tagged("post_install", "-at_install")
class TestWebsiteSale(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestWebsiteSale, cls).setUpClass()
        PaymentAcquirer = cls.env["payment.acquirer"]

        cls.payment_term_end_following_month = cls.env.ref(
            "account.account_payment_term_end_following_month"
        )
        cls.payment_term_30days = cls.env.ref("account.account_payment_term_30days")

        cls.website = cls.env["website"].browse(1)
        cls.WebsiteSaleController = WebsiteSale()
        cls.demo_user = cls.env.ref("base.user_demo")
        PaymentAcquirer.search([]).unlink()
        cls.acquirer_transfer_test_1 = PaymentAcquirer.create(
            {
                "name": "Test Transfer #1",
                "sequence": 10,
                "state": "test",
            }
        )
        cls.acquirer_transfer_test_2 = PaymentAcquirer.create(
            {
                "name": "Test Transfer #1",
                "sequence": 11,
                "state": "test",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
            }
        )

        cls.order = (
            cls.env["sale.order"]
            .with_user(cls.demo_user)
            .create(
                {
                    "partner_id": cls.demo_user.partner_id.id,
                    "order_line": [
                        (
                            0,
                            False,
                            {
                                "product_id": cls.product.id,
                                "name": cls.product.name,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                }
            )
        )

    def test_show_all_acquirers_with_display_main_payment_term_key(self):
        """
        This test covers the scenario when all acquirers have
        'display_main_payment_term' key and the customer have payment term
        """
        expected_acquirers = [
            self.acquirer_transfer_test_1,
            self.acquirer_transfer_test_2,
        ]
        self.acquirer_transfer_test_1.display_main_payment_term = True
        self.acquirer_transfer_test_2.display_main_payment_term = True
        self.demo_user.partner_id.write(
            {
                "property_payment_term_id": self.payment_term_30days.id,
            }
        )
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleController._get_shop_payment_values(self.order)
            self.assertListEqual(expected_acquirers, values.get("acquirers"))

    def test_skip_all_acquirers_with_display_main_payment_term_key(self):
        """
        This test covers the scenario when all acquirers have
        'display_main_payment_term' key and the customer doesn't have payment term
        """
        self.acquirer_transfer_test_1.display_main_payment_term = True
        self.acquirer_transfer_test_2.display_main_payment_term = True
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleController._get_shop_payment_values(self.order)
            self.assertListEqual([], values.get("acquirers"))

    def test_skip_acquirers_with_display_main_payment_term_key(self):
        """
        This test covers the scenario when 'Test Transfer #1' acquirer have
        'display_main_payment_term' key and the customer doesn't have payment term
        """
        expected_acquirers = [self.acquirer_transfer_test_2]
        self.acquirer_transfer_test_1.display_main_payment_term = True
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleController._get_shop_payment_values(self.order)
            self.assertListEqual(expected_acquirers, values.get("acquirers"))

    def test_show_default_acquirer_by_payment_term(self):
        """
        This test covers the scenario when all acquirers doesn't have
        'display_main_payment_term' key and the customer doesn't have payment term
        """
        expected_acquirers = [
            self.acquirer_transfer_test_1,
            self.acquirer_transfer_test_2,
        ]
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleController._get_shop_payment_values(self.order)
            self.assertListEqual(expected_acquirers, values.get("acquirers"))

    def test_show_acquirer_with_default_partner_term(self):
        """
        This test covers the scenario when all acquirers doesn't have
        'display_main_payment_term' key and the customer have payment term
        """
        expected_acquirers = [
            self.acquirer_transfer_test_1,
            self.acquirer_transfer_test_2,
        ]
        self.demo_user.partner_id.write(
            {
                "property_payment_term_id": self.payment_term_30days.id,
            }
        )
        with MockRequest(
            self.product.with_user(self.demo_user).env, website=self.website
        ):
            values = self.WebsiteSaleController._get_shop_payment_values(self.order)
            self.assertListEqual(expected_acquirers, values.get("acquirers"))
