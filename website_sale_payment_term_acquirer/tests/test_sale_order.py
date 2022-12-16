from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at-install")
class TestSaleOrder(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        PaymentAcquirer = cls.env["payment.acquirer"]

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

        cls.acquirer_transfer_test = PaymentAcquirer.create(
            {
                "name": "Test Transfer",
                "sequence": 10,
            }
        )
        cls.acquirer_transfer_test.journal_id = cls.company_data["default_journal_cash"]

        PaymentAcquirer.search([]).write({"display_main_payment_term": False})
        cls.partner_payment_term = cls.env.user.partner_id.property_payment_term_id

    def test_default_order_acquirer_position(self):
        """
        This test covers the behavior when a messages
        search have default ordering
        """
        first_acquirer = self.env["payment.acquirer"].search([], limit=1)
        self.assertNotEqual(first_acquirer, self.acquirer_transfer_test)

    def test_order_acquirer_with_flag(self):
        """
        This test covers the behavior when a message with key
        'display_main_payment_term' at search
        has a first position in the recordset
        """
        self.acquirer_transfer_test.write({"display_main_payment_term": True})
        first_acquirer = self.env["payment.acquirer"].search([], limit=1)
        self.assertEqual(first_acquirer, self.acquirer_transfer_test)

    def test_default_acquirer_behavior(self):
        """
        This test covers the behavior when a transaction creates by default. by default.
        """
        self.order._create_payment_transaction(
            {"acquirer_id": self.acquirer_transfer_test.id}
        )
        self.assertEqual(self.order.payment_term_id, self.partner_payment_term)

    def test_acquirer_behavior_with_tag(self):
        """
        This test covers the behavior when a transaction creates
        with the acquirer that has 'display_main_payment_term' key
        """
        self.acquirer_transfer_test.write({"display_main_payment_term": True})

        self.order._create_payment_transaction(
            {"acquirer_id": self.acquirer_transfer_test.id}
        )
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
        self.order._create_payment_transaction(
            {"acquirer_id": self.acquirer_transfer_test.id}
        )
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
        self.order._create_payment_transaction(
            {"acquirer_id": self.acquirer_transfer_test.id}
        )
        self.assertNotEqual(self.order.payment_term_id, self.partner_payment_term)
        self.assertEqual(self.order.payment_term_id, self.payment_term_30days)
