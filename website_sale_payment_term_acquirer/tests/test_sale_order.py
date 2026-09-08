from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale.controllers.payment import PaymentPortal


@tagged("post_install", "-at_install")
class TestSaleOrder(AccountTestInvoicingCommon, PaymentHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        PaymentAcquirer = cls.env["payment.provider"]

        cls.payment_term_end_following_month = cls.env.ref(
            "account.account_payment_term_end_following_month"
        )
        cls.payment_term_30days = cls.env.ref("account.account_payment_term_30days")

        cls.company_data["company"].country_id = cls.env.ref("base.us")

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product_a.id,
                            "name": "1 Product",
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )
        cls.order.carrier_id = cls.order._get_delivery_methods()[0]

        cls.acquirer_transfer_test = PaymentAcquirer.create(
            {
                "name": "Test Transfer",
                "sequence": 10,
            }
        )
        cls.acquirer_transfer_test.journal_id = cls.company_data["default_journal_cash"]
        # We need another test acquirer to check ordering
        cls.acquirer_transfer_test.copy()
        cls.payment_method = cls.env.ref("payment.payment_method_unknown")

        PaymentAcquirer.search([]).write({"display_main_payment_term": False})
        cls.partner_payment_term = cls.env.user.partner_id.property_payment_term_id = (
            cls.env.ref("account.account_payment_term_immediate")
        )
        cls.website = cls.env["website"].browse(1)
        cls.payment_portal = PaymentPortal()

    def _create_payment_transaction(self):
        with MockRequest(self.env):
            return self.make_jsonrpc_request(
                self._build_url(f"/shop/payment/transaction/{self.order.id}"),
                {
                    "order_id": self.order.id,
                    "access_token": self.order._portal_ensure_token(),
                    "provider_id": self.acquirer_transfer_test.id,
                    "payment_method_id": self.payment_method.id,
                    "token_id": None,
                    "flow": "direct",
                    "tokenization_requested": False,
                    "landing_route": None,
                },
            )

    def test_order_acquirer_with_flag(self):
        """
        This test covers the behavior when a message with key
        'display_main_payment_term' at search
        has a first position in the recordset
        """
        self.acquirer_transfer_test.write({"display_main_payment_term": True})
        all_acquirers = self.env["payment.provider"].search([])
        self.assertGreater(len(all_acquirers), 1)
        first_acquirer = all_acquirers[0]
        self.assertEqual(first_acquirer, self.acquirer_transfer_test)

    def test_default_acquirer_behavior(self):
        """
        This test covers the behavior when a transaction creates by default. by default.
        """
        self._create_payment_transaction()
        self.assertEqual(self.order.payment_term_id, self.partner_payment_term)

    def test_acquirer_behavior_with_tag(self):
        """
        This test covers the behavior when a transaction creates
        with the acquirer that has 'display_main_payment_term' key
        """
        self.acquirer_transfer_test.write({"display_main_payment_term": True})

        self._create_payment_transaction()
        self.assertEqual(self.order.payment_term_id, self.partner_payment_term)

    def test_acquirer_behavior_with_tag_and_payment_term(self):
        """
        This test covers the behavior when a transaction creates
        with the acquirer that has 'display_main_payment_term'
        key and has payment term
        """
        self.acquirer_transfer_test.write(
            {
                "display_main_payment_term": True,
                "payment_term_id": self.payment_term_30days.id,
            }
        )
        self._create_payment_transaction()
        self.assertEqual(self.order.payment_term_id, self.partner_payment_term)

    def test_acquirer_bevavior_with_payment_term(self):
        """This test covers the behavior when a transaction creates
        with the acquirer that hasn't 'display_main_payment_term'
        key and has payment term
        """
        self.acquirer_transfer_test.write(
            {
                "payment_term_id": self.payment_term_30days.id,
            }
        )
        self._create_payment_transaction()
        self.assertNotEqual(self.order.payment_term_id, self.partner_payment_term)
        self.assertEqual(self.order.payment_term_id, self.payment_term_30days)
