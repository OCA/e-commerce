# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from unittest.mock import patch
from urllib.parse import urlsplit

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment.tests.http_common import PaymentHttpCommon

from ..controllers.main import PayplugController
from .common import PayplugCommon, PayplugOAuth2Common

CONTROLLER_LOGGER = "odoo.addons.payment_payplug.controllers.main"
TX_LOGGER = "odoo.addons.payment_payplug.models.payment_transaction"
OTHER_LOGGERS = (
    "odoo.addons.payment.models.payment_provider",
    "odoo.addons.payment.models.payment_transaction",
)
LOGGERS = (CONTROLLER_LOGGER, TX_LOGGER, *OTHER_LOGGERS)


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

    @mute_logger(*LOGGERS)
    def test_webhook_body_not_an_object(self):
        tx = self._paid_tx()
        response = self._post_notification(
            [self._notification(self.fake_payplug.get_payment(tx.provider_reference))]
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(tx.state, "draft")
        self.assertEqual(len(self.fake_payplug.state.requests), 1)  # The creation.

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_webhook_without_object_id_is_ignored(self):
        for notification in (
            {"object": "payment"},
            {"object": "payment", "id": ""},
            {"object": "payment", "id": 42},
        ):
            with (
                self.subTest(notification=notification),
                self.assertLogs(TX_LOGGER, "WARNING") as logs,
            ):
                response = self._post_notification(notification)
                self.assertEqual(response.status_code, 200)
            self.assertIn("without object id", logs.output[0])
        self.assertFalse(self.fake_payplug.state.requests)

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_webhook_of_unknown_object_type_is_ignored(self):
        tx = self._paid_tx()
        with self.assertLogs(TX_LOGGER, "INFO") as logs:
            response = self._post_notification(
                {"id": tx.provider_reference, "object": "installment_plan"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Ignored Payplug notification of type installment_plan", logs.output[0]
        )
        self.assertEqual(tx.state, "draft")
        self.assertEqual(len(self.fake_payplug.state.requests), 1)  # The creation.

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

    def _open_hosted_url_without_payment(self, tx, key):
        """Open the return or cancel URL after the payment vanished from Payplug, so
        that every API request about it fails."""
        url = urlsplit(
            self.fake_payplug.get_payment(tx.provider_reference)["hosted_payment"][key]
        )
        del self.fake_payplug.state.payments[tx.provider_reference]
        with self.assertLogs(CONTROLLER_LOGGER, "ERROR") as logs:
            response = self.url_open(f"{url.path}?{url.query}", allow_redirects=False)
        # The customer is still redirected to the status page.
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/payment/status"))
        self.assertEqual(tx.state, "draft")
        return logs.output

    @mute_logger(TX_LOGGER, *OTHER_LOGGERS)
    def test_return_url_api_failure_still_redirects(self):
        tx = self._paid_tx()
        logs = self._open_hosted_url_without_payment(tx, "return_url")
        self.assertIn(f"Unable to fetch the Payplug payment of {tx.reference}", logs[0])

    @mute_logger(TX_LOGGER, *OTHER_LOGGERS)
    def test_cancel_url_api_failure_still_redirects(self):
        tx, _values = self._create_payplug_payment()
        logs = self._open_hosted_url_without_payment(tx, "cancel_url")
        self.assertIn(
            f"Unable to cancel the Payplug payment of {tx.reference}", logs[0]
        )
        # The abortion failed, then the reading of the payment.
        self.assertEqual(
            [request[0] for request in self.fake_payplug.state.requests],
            ["POST", "PATCH", "GET"],
        )

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

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_refund_notification_of_unknown_payment_is_ignored(self):
        for notification in (
            {"id": "re_unknown", "object": "refund", "payment_id": "pay_unknown"},
            {"id": "re_unknown", "object": "refund", "payment_id": 42},
            {"id": "re_unknown", "object": "refund"},
        ):
            with (
                self.subTest(notification=notification),
                self.assertLogs(TX_LOGGER, "WARNING") as logs,
            ):
                response = self._post_notification(notification)
                self.assertEqual(response.status_code, 200)
            self.assertIn("No Payplug transaction found for refund", logs.output[0])
        self.assertFalse(self.fake_payplug.state.requests)

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_refund_notification_not_matching_its_payment_is_ignored(self):
        tx = self._done_tx()
        refund = self.fake_payplug.create_refund(tx.provider_reference, 1000)
        # Defensive check: the API returns a refund of another payment.
        inconsistent_refund = dict(refund, payment_id="pay_another_payment")
        with (
            patch.object(
                type(tx), "_payplug_get_refund", return_value=inconsistent_refund
            ),
            self.assertLogs(TX_LOGGER, "WARNING") as logs,
        ):
            response = self._post_notification(self._notification(refund))
        self.assertEqual(response.status_code, 200)
        self.assertIn("does not match its payment", logs.output[0])
        self.assertFalse(tx.child_transaction_ids)

    @mute_logger(*LOGGERS)
    def test_refund_notification_completes_odoo_refund_with_lost_response(self):
        tx = self._done_tx()
        # The refund request reached Payplug, but its response was lost: the refund
        # transaction has no Payplug id.
        refund_tx = tx._create_child_transaction(10.0, is_refund=True)
        refund = self.fake_payplug.create_refund(
            tx.provider_reference,
            1000,
            metadata={"odoo_reference": refund_tx.reference},
        )
        response = self._post_notification(self._notification(refund))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tx.child_transaction_ids, refund_tx)
        self.assertEqual(refund_tx.state, "done")
        self.assertEqual(refund_tx.provider_reference, refund["id"])

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_refund_notification_of_odoo_refund_in_progress_is_left_to_odoo(self):
        tx = self._done_tx()
        # Refund requested by Odoo, whose transaction is not committed yet.
        refund = self.fake_payplug.create_refund(
            tx.provider_reference,
            1000,
            metadata={"odoo_reference": f"R-{tx.reference}-in-progress"},
        )
        with self.assertLogs(TX_LOGGER, "INFO") as logs:
            response = self._post_notification(self._notification(refund))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any("is being processed by Odoo" in line for line in logs.output)
        )
        self.assertFalse(tx.child_transaction_ids)

    @mute_logger(CONTROLLER_LOGGER, *OTHER_LOGGERS)
    def test_refund_notification_of_unconfirmed_payment_is_ignored(self):
        tx = self._paid_tx()  # Paid on Payplug, not confirmed in Odoo yet.
        refund = self.fake_payplug.create_refund(tx.provider_reference, 1000)
        with self.assertLogs(TX_LOGGER, "WARNING") as logs:
            response = self._post_notification(self._notification(refund))
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"unconfirmed transaction {tx.reference}", logs.output[0])
        self.assertFalse(tx.child_transaction_ids)
        self.assertEqual(tx.state, "draft")


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
