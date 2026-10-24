# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import Command
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.account_payment.tests.common import AccountPaymentCommon

from .common import PayplugCommon

LOGGERS = (
    "odoo.addons.payment_payplug.models.payment_transaction",
    "odoo.addons.payment.models.payment_provider",
    "odoo.addons.payment.models.payment_transaction",
)


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugInvoice(PayplugCommon, AccountPaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payplug.journal_id = cls.company_data["default_journal_bank"]
        cls.invoice = cls.init_invoice(
            "out_invoice", partner=cls.partner, amounts=[120.0], taxes=[], post=True
        )

    @mute_logger(*LOGGERS)
    def test_invoice_payment_and_partial_refund(self):
        self.assertEqual(self.invoice.amount_total, 120.0)
        tx, _values = self._create_payplug_payment(
            amount=self.invoice.amount_total,
            reference=None,
            invoice_ids=[Command.set(self.invoice.ids)],
        )
        self.assertIn(self.invoice.name, tx.reference)
        self.fake_payplug.mark_paid(tx.provider_reference)
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")

        tx._post_process()
        self.assertTrue(tx.payment_id)
        self.assertEqual(tx.payment_id.amount, 120.0)
        self.assertIn(self.invoice.payment_state, ("in_payment", "paid"))

        # Partial refund from the payment, as with the "Refund" button of the payment.
        wizard = (
            self.env["payment.refund.wizard"]
            .with_context(active_model="account.payment", active_id=tx.payment_id.id)
            .create({})
        )
        self.assertEqual(wizard.support_refund, "partial")
        wizard.amount_to_refund = 20.0
        wizard.action_refund()
        refund_tx = tx.child_transaction_ids
        self.assertEqual(refund_tx.state, "done")
        self.assertAlmostEqual(refund_tx.amount, -20.0)
        refund_tx._post_process()
        self.assertTrue(refund_tx.payment_id)
        tx.payment_id.invalidate_recordset(["amount_available_for_refund"])
        self.assertAlmostEqual(tx.payment_id.amount_available_for_refund, 100.0)
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertEqual(payment["amount_refunded"], 2000)
