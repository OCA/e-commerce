# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from urllib.parse import urlsplit

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment.tests.http_common import PaymentHttpCommon

from ..controllers.main import PayplugController
from .common import PayplugCommon, PayplugOAuth2Common

LOGGERS = (
    "odoo.addons.payment_payplug.controllers.main",
    "odoo.addons.payment_payplug.models.payment_transaction",
    "odoo.addons.payment.models.payment_provider",
    "odoo.addons.payment.models.payment_transaction",
)


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugHttp(PayplugCommon, PaymentHttpCommon):
    def _post_notification(self, data):
        url = self._build_url(PayplugController._webhook_url)
        return self.url_open(url, json=data)

    def _open_hosted_url(self, tx, key):
        """Open the return or cancel URL given to Payplug, without the redirection."""
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        url = urlsplit(payment["hosted_payment"][key])
        return self.url_open(f"{url.path}?{url.query}", allow_redirects=False)

    def _paid_tx(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference)
        return tx

    # === Payment notifications === #

    @mute_logger(*LOGGERS)
    def test_webhook_confirms_payment(self):
        tx = self._paid_tx()
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        response = self._post_notification(self._notification(payment))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.state, "done")

    @mute_logger(*LOGGERS)
    def test_webhook_forged_body_is_not_trusted(self):
        tx, _values = self._create_payplug_payment()
        payment = dict(self.fake_payplug.get_payment(tx.provider_reference))
        # The forged body claims the payment is paid; the API says otherwise.
        payment.update(is_paid=True, paid_at=1700000000)
        response = self._post_notification(payment)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.state, "pending")

    @mute_logger(*LOGGERS)
    def test_webhook_unknown_payment_is_ignored(self):
        tx = self._paid_tx()
        response = self._post_notification(
            {"id": "pay_unknown", "object": "payment", "is_live": False}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.state, "draft")
        # No API request was sent for the unknown payment.
        self.assertNotIn(
            "/v1/payments/pay_unknown", [r[1] for r in self.fake_payplug.state.requests]
        )

    @mute_logger(*LOGGERS)
    def test_webhook_replay_is_idempotent(self):
        tx = self._paid_tx()
        notification = self._notification(
            self.fake_payplug.get_payment(tx.provider_reference)
        )
        self._post_notification(notification)
        self.assertEqual(tx.state, "done")
        last_state_change = tx.last_state_change
        messages = self.env["mail.message"].search_count([])
        response = self._post_notification(notification)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.state, "done")
        self.assertEqual(tx.last_state_change, last_state_change)
        self.assertEqual(self.env["mail.message"].search_count([]), messages)

    @mute_logger(*LOGGERS)
    def test_webhook_invalid_body(self):
        url = self._build_url(PayplugController._webhook_url)
        response = self.url_open(
            url, data="not json", headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 400)

    @mute_logger(*LOGGERS)
    def test_webhook_api_failure_asks_for_retry(self):
        tx = self._paid_tx()
        notification = self._notification(
            self.fake_payplug.get_payment(tx.provider_reference)
        )
        del self.fake_payplug.state.payments[tx.provider_reference]
        response = self._post_notification(notification)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(tx.state, "draft")

    # === Customer redirections === #

    @mute_logger(*LOGGERS)
    def test_return_url_processes_payment(self):
        tx = self._paid_tx()
        response = self._open_hosted_url(tx, "return_url")
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/payment/status"))
        self.assertEqual(tx.state, "done")

    @mute_logger(*LOGGERS)
    def test_return_url_with_invalid_token_is_ignored(self):
        tx = self._paid_tx()
        url = self._build_url(PayplugController._return_url)
        response = self.url_open(
            f"{url}?reference={tx.reference}&access_token=forged", allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(tx.state, "draft")

    @mute_logger(*LOGGERS)
    def test_cancel_url_aborts_payment(self):
        tx, _values = self._create_payplug_payment()
        response = self._open_hosted_url(tx, "cancel_url")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(tx.state, "cancel")
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertEqual(payment["failure"]["code"], "aborted")

    # === Refund notifications === #

    def _done_tx(self):
        tx = self._paid_tx()
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        return tx

    @mute_logger(*LOGGERS)
    def test_refund_from_payplug_portal_creates_refund_transaction(self):
        tx = self._done_tx()
        refund = self.fake_payplug.create_refund(
            tx.provider_reference, 1000
        )  # No metadata.
        response = self._post_notification(self._notification(refund))
        self.assertEqual(response.status_code, 200)
        refund_tx = tx.child_transaction_ids
        self.assertEqual(len(refund_tx), 1)
        self.assertEqual(refund_tx.operation, "refund")
        self.assertEqual(refund_tx.state, "done")
        self.assertAlmostEqual(refund_tx.amount, -10.0)
        self.assertEqual(refund_tx.provider_reference, refund["id"])

        # A replayed notification does not create a second refund.
        self._post_notification(self._notification(refund))
        self.assertEqual(len(tx.child_transaction_ids), 1)

    @mute_logger(*LOGGERS)
    def test_refund_notification_of_odoo_refund_is_not_duplicated(self):
        tx = self._done_tx()
        tx.action_refund(amount_to_refund=5.0)
        refund_tx = tx.child_transaction_ids
        refund = self.fake_payplug.state.refunds[refund_tx.provider_reference]
        self._post_notification(self._notification(refund))
        self.assertEqual(tx.child_transaction_ids, refund_tx)
        self.assertEqual(refund_tx.state, "done")

    @mute_logger(*LOGGERS)
    def test_refund_notification_with_forged_payment_id_is_ignored(self):
        tx = self._done_tx()
        other_tx = self._done_tx_with_reference("other-reference")
        refund = self.fake_payplug.create_refund(tx.provider_reference, 1000)
        notification = self._notification(refund)
        notification["payment_id"] = (
            other_tx.provider_reference
        )  # Points to the wrong payment.
        self._post_notification(notification)
        self.assertFalse(other_tx.child_transaction_ids)
        self.assertFalse(tx.child_transaction_ids)

    def _done_tx_with_reference(self, reference):
        tx, _values = self._create_payplug_payment(reference=reference)
        self.fake_payplug.mark_paid(tx.provider_reference)
        tx._payplug_fetch_and_process()
        return tx


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugOAuth2Http(PayplugOAuth2Common, PaymentHttpCommon):
    @mute_logger(*LOGGERS)
    def test_webhook_with_oauth2(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        url = self._build_url(PayplugController._webhook_url)
        response = self.url_open(url, json=self._notification(payment))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.state, "done")
        # The request served by the HTTP worker thread reused the cached token.
        self.assertEqual(len(self.fake_payplug.state.token_requests), 1)
        self.assertEqual(len(self.fake_payplug.state.requests), 2)
