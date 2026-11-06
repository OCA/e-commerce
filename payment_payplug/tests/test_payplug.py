# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import json
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import requests

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .. import const
from .common import PayplugCommon

TX_LOGGER = "odoo.addons.payment_payplug.models.payment_transaction"
LOGGERS = (
    TX_LOGGER,
    "odoo.addons.payment.models.payment_provider",
    "odoo.addons.payment.models.payment_transaction",
)


def _make_response(status_code, body):
    """Return a `requests` response with the given status and body (bytes or JSON)."""
    response = requests.models.Response()
    response.status_code = status_code
    response.encoding = "utf-8"
    response._content = body if isinstance(body, bytes) else json.dumps(body).encode()
    return response


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugProvider(PayplugCommon):
    def test_supported_currencies_are_eur_only(self):
        self.assertEqual(self.payplug.available_currency_ids, self.currency_euro)
        compatible = self.env["payment.provider"]._get_compatible_providers(
            self.company.id,
            self.partner.id,
            self.amount,
            currency_id=self.currency_euro.id,
        )
        self.assertIn(self.payplug, compatible)
        incompatible = self.env["payment.provider"]._get_compatible_providers(
            self.company.id,
            self.partner.id,
            self.amount,
            currency_id=self.currency_usd.id,
        )
        self.assertNotIn(self.payplug, incompatible)

    def test_feature_support(self):
        self.assertEqual(self.payplug.support_refund, "partial")
        self.assertFalse(self.payplug.support_tokenization)
        self.assertFalse(self.payplug.support_manual_capture)

    def test_secret_key_restricted_to_system_group(self):
        field = self.env["payment.provider"]._fields["payplug_secret_key"]
        self.assertEqual(field.groups, "base.group_system")
        with self.assertRaises(AccessError):
            self.payplug.with_user(self.internal_user).read(["payplug_secret_key"])

    def test_secret_key_must_match_state(self):
        with self.assertRaises(ValidationError):
            self.payplug.write({"payplug_secret_key": "sk_live_whatever"})
        with self.assertRaises(ValidationError):
            self.payplug.write({"state": "enabled"})
        self.payplug.write(
            {"state": "enabled", "payplug_secret_key": "sk_live_whatever"}
        )
        self.assertEqual(self.payplug.state, "enabled")

    def test_reset_credentials_clears_secret_key(self):
        self.payplug.action_reset_credentials()
        self.assertFalse(self.payplug.payplug_secret_key)
        self.assertEqual(self.payplug.state, "disabled")

    def test_default_api_url(self):
        self.env["ir.config_parameter"].sudo().set_param(
            const.API_BASE_URL_PARAM, False
        )
        self.assertEqual(
            self.payplug._build_request_url("payments"),
            "https://api.payplug.com/v1/payments",
        )

    def test_other_providers_are_not_affected(self):
        other = self.dummy_provider
        self.assertEqual(other._get_default_payment_method_codes(), set())
        self.assertEqual(other._build_request_url("payments"), "")
        # The Payplug credentials are never sent to another provider.
        self.assertEqual(other._build_request_headers("GET", "payments", None), {})
        response = _make_response(
            400, {"message": "Invalid parameters.", "details": {"amount": "Too low."}}
        )
        self.assertEqual(other._parse_response_error(response), response.text)
        self.assertEqual(
            self.payplug._parse_response_error(response),
            "Invalid parameters. {'amount': 'Too low.'}",
        )

    @mute_logger(*LOGGERS)
    def test_error_response_without_json_object(self):
        # E.g. the HTML page of a proxy, or an unexpected JSON value.
        for body, expected in (
            (b"<html>502 Bad Gateway</html>", "<html>502 Bad Gateway</html>"),
            (["unexpected"], '["unexpected"]'),
            ({"object": "error"}, '{"object": "error"}'),
        ):
            with self.subTest(body=body):
                response = _make_response(502, body)
                self.assertEqual(self.payplug._parse_response_error(response), expected)
        response = _make_response(502, b"<html>502 Bad Gateway</html>")
        with (
            patch.object(requests, "request", return_value=response),
            self.assertRaisesRegex(ValidationError, "502 Bad Gateway"),
        ):
            self.payplug._send_api_request("GET", "payments/pay_unknown")


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugPayment(PayplugCommon):
    def _last_request(self):
        method, path, headers, body = self.fake_payplug.state.requests[-1]
        return method, path, headers, json.loads(body) if body else {}

    def test_payment_creation_and_redirect_form(self):
        tx, processing_values = self._create_payplug_payment()

        method, path, headers, payload = self._last_request()
        self.assertEqual((method, path), ("POST", "/v1/payments"))
        self.assertEqual(
            headers["Authorization"], "Bearer sk_test_odoo_payplug_fake_key"
        )
        self.assertEqual(headers["PayPlug-Version"], const.API_VERSION)
        self.assertEqual(payload["amount"], 4990)
        self.assertEqual(payload["currency"], "EUR")
        self.assertEqual(payload["metadata"], {"odoo_reference": tx.reference})
        self.assertNotIn(
            "payment_method", payload
        )  # Card: the default of the payment page.
        self.assertTrue(
            payload["notification_url"].endswith("/payment/payplug/webhook")
        )
        for key, route in (("return_url", "return"), ("cancel_url", "cancel")):
            url = urlsplit(payload["hosted_payment"][key])
            self.assertEqual(url.path, f"/payment/payplug/{route}")
            params = parse_qs(url.query)
            self.assertEqual(params["reference"], [tx.reference])
            self.assertEqual(
                params["access_token"], [self._generate_test_access_token(tx.reference)]
            )
        self.assertEqual(payload["billing"]["email"], "norbert.buyer@example.com")
        self.assertEqual(payload["billing"]["country"], "BE")
        self.assertEqual(payload["billing"]["language"], "en")
        self.assertEqual(payload["shipping"]["delivery_type"], "BILLING")
        # "0032 12 34 56 78" is international (00 prefix), not a French mobile.
        self.assertEqual(payload["billing"]["landline_phone_number"], "+3212345678")
        self.assertNotIn("mobile_phone_number", payload["billing"])

        payment = self.fake_payplug.get_payment(tx.provider_reference)
        form = self._extract_values_from_html_form(
            processing_values["redirect_form_html"]
        )
        self.assertEqual(form["action"], payment["hosted_payment"]["payment_url"])
        self.assertEqual(form["method"], "get")
        self.assertEqual(tx.state, "draft")

    def test_alternative_payment_method_is_sent(self):
        bancontact = self.env.ref("payment.payment_method_bancontact")
        bancontact.active = True
        self._create_payplug_payment(payment_method_id=bancontact.id)
        payload = self._last_request()[3]
        self.assertEqual(payload["payment_method"], "bancontact")

    def test_phone_formatting(self):
        tx_model = self.env["payment.transaction"]
        self.assertEqual(
            tx_model._payplug_format_phone("+33 6 12 34 56 78"), "+33612345678"
        )
        self.assertEqual(
            tx_model._payplug_format_phone("0033 3 88 12 34 56"), "+33388123456"
        )
        # Local numbers are not sent: their country cannot be guessed safely.
        self.assertIsNone(tx_model._payplug_format_phone("06 12 34 56 78"))
        self.partner.phone = "+33 6 12 34 56 78"
        self._create_payplug_payment()
        billing = self._last_request()[3]["billing"]
        self.assertEqual(billing["mobile_phone_number"], "+33612345678")

    @mute_logger(*LOGGERS)
    def test_amount_below_minimum_is_refused_before_any_request(self):
        tx, _values = self._create_payplug_payment(amount=0.29)
        self.assertEqual(tx.state, "error")
        self.assertFalse(self.fake_payplug.state.requests)

    @mute_logger(*LOGGERS)
    def test_api_rejection_sets_error(self):
        bancontact = self.env.ref("payment.payment_method_bancontact")
        bancontact.active = True
        # No local check for alternative methods: the (fake) API refuses the amount.
        tx, _values = self._create_payplug_payment(
            amount=30000.00, payment_method_id=bancontact.id
        )
        self.assertEqual(tx.state, "error")
        self.assertIn("Invalid parameters", tx.state_message)

    @mute_logger(*LOGGERS)
    def test_paid_payment_confirms_transaction(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference, brand="Visa")
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        self.assertEqual(tx.payment_method_id.code, "visa")
        self.assertEqual(
            self.fake_payplug.state.requests[-1][:2],
            ("GET", f"/v1/payments/{tx.provider_reference}"),
        )

    @mute_logger(*LOGGERS)
    def test_unpaid_payment_sets_pending(self):
        tx, _values = self._create_payplug_payment()
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "pending")

    @mute_logger(*LOGGERS)
    def test_failed_payment_sets_error(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_failed(
            tx.provider_reference, "card_declined", "Declined."
        )
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "error")
        self.assertIn("card_declined", tx.state_message)

    @mute_logger(*LOGGERS)
    def test_timed_out_payment_cancels_transaction(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_failed(tx.provider_reference, "timeout", "Timeout.")
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "cancel")

    @mute_logger(*LOGGERS)
    def test_customer_cancellation_aborts_payment(self):
        tx, _values = self._create_payplug_payment()
        tx._payplug_abort_and_process()
        self.assertEqual(tx.state, "cancel")
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertEqual(payment["failure"]["code"], "aborted")

    @mute_logger(*LOGGERS)
    def test_cancellation_of_paid_payment_keeps_it_paid(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference)
        tx._payplug_abort_and_process()
        self.assertEqual(tx.state, "done")

    @mute_logger(*LOGGERS)
    def test_amount_mismatch_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        payment["amount"] = 100
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "error")

    @mute_logger(*LOGGERS)
    def test_currency_mismatch_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        payment["currency"] = "USD"
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "error")

    @mute_logger(*LOGGERS)
    def test_reference_mismatch_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        payment["metadata"] = {"odoo_reference": "another-reference"}
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "error")

    @mute_logger(*LOGGERS)
    def test_live_payment_on_test_provider_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        # The fake API hides live payments from test keys: process the data directly.
        tx._process("payplug", dict(payment, is_live=True))
        self.assertEqual(tx.state, "error")

    @mute_logger(*LOGGERS)
    def test_other_object_than_payment_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        tx._process("payplug", dict(payment, object="refund"))
        self.assertEqual(tx.state, "error")
        self.assertIn("not a payment", tx.state_message)

    @mute_logger(*LOGGERS)
    def test_payment_id_mismatch_sets_error(self):
        tx, _values = self._create_payplug_payment()
        payment = self.fake_payplug.mark_paid(tx.provider_reference)
        tx._process("payplug", dict(payment, id="pay_another_payment"))
        self.assertEqual(tx.state, "error")
        self.assertIn("payment id does not match", tx.state_message)

    @mute_logger(*LOGGERS)
    def test_missing_payment_page_url_sets_error(self):
        payment_data = {"id": "pay_without_url", "object": "payment"}
        with patch.object(
            type(self.payplug), "_send_api_request", return_value=payment_data
        ):
            tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "error")
        self.assertIn("did not return any payment page URL", tx.state_message)
        # The payment id is kept, to match the later notifications of the payment.
        self.assertEqual(tx.provider_reference, "pay_without_url")

    def test_empty_customer_values_are_not_sent(self):
        self.partner.write({"phone": False, "street2": False, "city": "X" * 150})
        self._create_payplug_payment()
        billing = self._last_request()[3]["billing"]
        self.assertNotIn("mobile_phone_number", billing)
        self.assertNotIn("landline_phone_number", billing)
        self.assertNotIn("address2", billing)
        self.assertEqual(billing["city"], "X" * const.FIELD_MAX_LENGTHS["city"])
        self.assertIsNone(self.env["payment.transaction"]._payplug_format_phone(False))

    def test_fetch_without_payplug_id_sends_no_request(self):
        tx = self._create_transaction("redirect")
        with self.assertLogs(TX_LOGGER, "WARNING") as logs:
            tx._payplug_fetch_and_process()
        self.assertIn("has no Payplug payment id", logs.output[0])
        self.assertEqual(tx.state, "draft")
        self.assertFalse(self.fake_payplug.state.requests)

    @mute_logger(*LOGGERS)
    def test_cancellation_without_payment_or_once_processed_sends_no_request(self):
        draft_tx = self._create_transaction("redirect")  # No payment on Payplug.
        draft_tx._payplug_abort_and_process()
        self.assertEqual(draft_tx.state, "draft")
        self.assertFalse(self.fake_payplug.state.requests)

        tx, _values = self._create_payplug_payment(reference="paid-reference")
        self.fake_payplug.mark_paid(tx.provider_reference)
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        requests_count = len(self.fake_payplug.state.requests)
        # E.g. the customer opens the cancel URL after paying.
        tx._payplug_abort_and_process()
        self.assertEqual(tx.state, "done")
        self.assertEqual(len(self.fake_payplug.state.requests), requests_count)

    def test_other_providers_transactions_are_not_affected(self):
        payplug_like_data = {
            "reference": "dummy-reference",
            "object": "payment",
            "is_paid": True,
            "amount": 4990,
            "currency": "EUR",
            "metadata": {"odoo_reference": "another-reference"},
        }
        tx_model = self.env["payment.transaction"]
        self.assertEqual(
            tx_model._extract_reference("none", payplug_like_data), "dummy-reference"
        )
        dummy_tx = self._create_transaction(
            "redirect",
            provider_id=self.dummy_provider.id,
            payment_method_id=self.dummy_provider.payment_method_ids[:1].id,
            reference="dummy-reference",
        )
        self.assertEqual(dummy_tx._get_specific_rendering_values({}), {})
        self.assertEqual(dummy_tx._extract_amount_data(payplug_like_data), {})
        dummy_tx._apply_updates(payplug_like_data)
        self.assertEqual(dummy_tx.state, "draft")
        dummy_tx._send_refund_request()
        self.assertFalse(self.fake_payplug.state.requests)


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugRefreshStatus(PayplugCommon):
    @mute_logger(*LOGGERS)
    def test_refresh_status(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference)
        dummy_tx = self._create_transaction(
            "redirect",
            provider_id=self.dummy_provider.id,
            payment_method_id=self.dummy_provider.payment_method_ids[:1].id,
            reference="dummy-reference",
        )
        action = (tx + dummy_tx).action_payplug_refresh_status()
        self.assertEqual(action, {"type": "ir.actions.client", "tag": "soft_reload"})
        self.assertEqual(tx.state, "done")
        self.assertEqual(dummy_tx.state, "draft")
        # The creation and one reading, for the Payplug transaction only.
        self.assertEqual(len(self.fake_payplug.state.requests), 2)

    @mute_logger(*LOGGERS)
    def test_refresh_status_reports_api_errors(self):
        tx, _values = self._create_payplug_payment()
        del self.fake_payplug.state.payments[tx.provider_reference]
        action = tx.action_payplug_refresh_status()
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "danger")
        self.assertIn("could not be found", action["params"]["message"])
        self.assertEqual(tx.state, "draft")

    def test_refresh_status_requires_write_access(self):
        tx, _values = self._create_payplug_payment()
        with self.assertRaises(AccessError):
            tx.with_user(self.internal_user).action_payplug_refresh_status()
        self.assertEqual(len(self.fake_payplug.state.requests), 1)


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugRefund(PayplugCommon):
    def _create_paid_transaction(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference)
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        return tx

    @mute_logger(*LOGGERS)
    def test_full_refund(self):
        tx = self._create_paid_transaction()
        tx.action_refund()
        refund_tx = tx.child_transaction_ids
        self.assertEqual(len(refund_tx), 1)
        self.assertEqual(refund_tx.operation, "refund")
        self.assertEqual(refund_tx.state, "done")
        self.assertAlmostEqual(refund_tx.amount, -self.amount)
        self.assertTrue(refund_tx.provider_reference.startswith("re_"))
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertTrue(payment["is_refunded"])
        refund = self.fake_payplug.state.refunds[refund_tx.provider_reference]
        self.assertEqual(refund["amount"], 4990)
        self.assertEqual(refund["metadata"], {"odoo_reference": refund_tx.reference})

    @mute_logger(*LOGGERS)
    def test_partial_refunds(self):
        tx = self._create_paid_transaction()
        tx.action_refund(amount_to_refund=10.00)
        tx.action_refund(amount_to_refund=15.50)
        refund_txs = tx.child_transaction_ids
        self.assertEqual(len(refund_txs), 2)
        self.assertEqual(set(refund_txs.mapped("state")), {"done"})
        self.assertAlmostEqual(sum(refund_txs.mapped("amount")), -25.50)
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertEqual(payment["amount_refunded"], 2550)
        self.assertFalse(payment["is_refunded"])

    @mute_logger(*LOGGERS)
    def test_refund_above_remaining_amount_sets_error(self):
        tx = self._create_paid_transaction()
        tx.action_refund(amount_to_refund=40.00)
        tx.action_refund(amount_to_refund=20.00)
        failed = tx.child_transaction_ids.filtered(lambda t: t.state == "error")
        self.assertEqual(len(failed), 1)
        self.assertIn("refundable amount", failed.state_message)

    @mute_logger(*LOGGERS)
    def test_refund_below_minimum_sets_error(self):
        tx = self._create_paid_transaction()
        tx.action_refund(amount_to_refund=0.05)
        refund_tx = tx.child_transaction_ids
        self.assertEqual(refund_tx.state, "error")
        self.assertFalse(self.fake_payplug.state.refunds)

    @mute_logger(*LOGGERS)
    def test_refund_data_not_matching_the_refund_sets_error(self):
        tx = self._create_paid_transaction()
        for name, changes in (
            ("object", {"object": "payment"}),
            ("payment", {"payment_id": "pay_another_payment"}),
            ("id", {"id": "re_another_refund"}),
            ("environment", {"is_live": True}),
        ):
            with self.subTest(name=name):
                refund_tx = tx._create_child_transaction(10.0, is_refund=True)
                refund = self.fake_payplug.create_refund(
                    tx.provider_reference,
                    1000,
                    metadata={"odoo_reference": refund_tx.reference},
                )
                refund_tx.provider_reference = refund["id"]
                refund_tx._process("payplug", dict(refund, **changes))
                self.assertEqual(refund_tx.state, "error")
                self.assertIn(
                    "environment" if name == "environment" else "does not match",
                    refund_tx.state_message,
                )
                self.assertEqual(refund_tx.provider_reference, refund["id"])
