# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import base64
import threading
from unittest.mock import Mock, patch
from urllib.parse import parse_qs

import requests

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .. import const, oauth
from .common import (
    LIVE_CLIENT_ID,
    LIVE_CLIENT_SECRET,
    TEST_CLIENT_ID,
    TEST_CLIENT_SECRET,
    TEST_SECRET_KEY,
    PayplugOAuth2Common,
)

LOGGERS = (
    "odoo.addons.payment_payplug.models.payment_provider",
    "odoo.addons.payment_payplug.models.payment_transaction",
    "odoo.addons.payment.models.payment_provider",
    "odoo.addons.payment.models.payment_transaction",
)

REQUESTS_POST = "odoo.addons.payment_payplug.models.payment_provider.requests.post"


@tagged("post_install", "-at_install", "payment_payplug")
class TestPayplugOAuth2(PayplugOAuth2Common):
    # === Helpers === #

    def _token_requests(self):
        return self.fake_payplug.state.token_requests

    def _api_requests(self):
        return self.fake_payplug.state.requests

    def _api_tokens(self):
        """Return the bearer tokens of the API requests, in order."""
        return [
            headers["Authorization"].removeprefix("Bearer ")
            for _method, _path, headers, _body in self._api_requests()
        ]

    def _paid_tx(self):
        tx, _values = self._create_payplug_payment()
        self.fake_payplug.mark_paid(tx.provider_reference)
        return tx

    # === Token request === #

    def test_token_request(self):
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "draft")
        self.assertTrue(tx.provider_reference)

        self.assertEqual(len(self._token_requests()), 1)
        headers, body = self._token_requests()[0]
        credentials = base64.b64encode(
            f"{TEST_CLIENT_ID}:{TEST_CLIENT_SECRET}".encode()
        ).decode()
        self.assertEqual(headers["Authorization"], f"Basic {credentials}")
        self.assertEqual(headers["Content-Type"], "application/x-www-form-urlencoded")
        self.assertEqual(
            parse_qs(body.decode()),
            {
                "grant_type": ["client_credentials"],
                "audience": [const.DEFAULT_TOKEN_AUDIENCE],
            },
        )

        token = self.fake_payplug.issued_tokens()[0]
        method, path, api_headers, _body = self._api_requests()[-1]
        self.assertEqual((method, path), ("POST", "/v1/payments"))
        self.assertEqual(api_headers["Authorization"], f"Bearer {token}")
        self.assertEqual(api_headers["PayPlug-Version"], const.API_VERSION)

    def test_default_token_url_and_audience(self):
        self.assertEqual(
            self.payplug._payplug_get_token_url(),
            self.fake_payplug.api_url.replace("/v1/", "/oauth2/token"),
        )
        self.env["ir.config_parameter"].sudo().set_param(
            const.API_BASE_URL_PARAM, False
        )
        self.assertEqual(
            self.payplug._payplug_get_token_url(),
            "https://api.payplug.com/oauth2/token",
        )
        self.assertEqual(
            self.payplug._payplug_get_token_audience(), "https://www.payplug.com"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            const.TOKEN_URL_PARAM, "http://127.0.0.1:1/token"
        )
        self.assertEqual(
            self.payplug._payplug_get_token_url(), "http://127.0.0.1:1/token"
        )

    @mute_logger(*LOGGERS)
    def test_whole_flow_with_oauth2(self):
        tx = self._paid_tx()
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        tx.action_refund(amount_to_refund=10.0)
        refund_tx = tx.child_transaction_ids
        self.assertEqual(refund_tx.state, "done")
        other_tx, _values = self._create_payplug_payment(reference="other-ref")
        other_tx._payplug_abort_and_process()
        self.assertEqual(other_tx.state, "cancel")
        # One token for all the requests: creations, reading, refund, abortion.
        self.assertEqual(len(self._token_requests()), 1)
        self.assertEqual(len(self._api_requests()), 5)
        self.assertEqual(
            set(self._api_tokens()), set(self.fake_payplug.issued_tokens())
        )

    # === Cache === #

    @mute_logger(*LOGGERS)
    def test_token_is_cached(self):
        tx = self._paid_tx()
        tx._payplug_fetch_and_process()
        tx._payplug_fetch_and_process()
        self._create_payplug_payment(reference="second-ref")
        self.assertEqual(len(self._token_requests()), 1)
        self.assertEqual(len(set(self._api_tokens())), 1)

    def test_cache_key_does_not_hold_secrets(self):
        self.payplug._payplug_get_access_token()
        (key,) = oauth.TOKEN_CACHE.keys()
        self.assertEqual(key[:2], (self.env.cr.dbname, self.payplug.id))
        self.assertNotIn(TEST_CLIENT_SECRET, repr(key))
        self.assertNotIn(TEST_CLIENT_ID, repr(key))

    @mute_logger(*LOGGERS)
    def test_token_renewed_before_expiry(self):
        start = oauth.now()
        with patch.object(oauth, "now", return_value=start):
            tx = self._paid_tx()
        # The token lives 299 s and is renewed 60 s before its expiry.
        with patch.object(oauth, "now", return_value=start + 238):
            tx._payplug_fetch_and_process()
        self.assertEqual(len(self._token_requests()), 1)
        with patch.object(oauth, "now", return_value=start + 240):
            tx._payplug_fetch_and_process()
        self.assertEqual(len(self._token_requests()), 2)
        first, second = self.fake_payplug.issued_tokens()
        self.assertEqual(self._api_tokens(), [first, first, second])

    @mute_logger(*LOGGERS)
    def test_short_token_renewed_at_half_life(self):
        self.fake_payplug.state.token_lifetime = 30
        start = oauth.now()
        with patch.object(oauth, "now", return_value=start):
            self.payplug._payplug_get_access_token()
        with patch.object(oauth, "now", return_value=start + 14):
            self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 1)
        with patch.object(oauth, "now", return_value=start + 16):
            self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 2)

    def test_cache_invalidated_on_credentials_change(self):
        self.payplug._payplug_get_access_token()
        self.payplug.name = "Payplug (renamed)"
        self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 1)
        self.payplug.payplug_client_secret = TEST_CLIENT_SECRET
        self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 2)

    def test_concurrent_requests_fetch_one_token(self):
        cache = oauth.TokenCache(renewal_margin=60)
        calls = []
        barrier = threading.Barrier(5)

        def fetch():
            calls.append(1)
            threading.Event().wait(0.1)
            return f"token-{len(calls)}", 299, oauth.MODE_TEST, "test"

        results = []

        def worker():
            barrier.wait()
            results.append(cache.get_or_fetch(("db", 1, "h"), b"fp", fetch).value)

        threads = [threading.Thread(target=worker) for _i in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(len(calls), 1)
        self.assertEqual(results, ["token-1"] * 5)
        # Another secret (other fingerprint) gets another token.
        self.assertEqual(
            cache.get_or_fetch(("db", 1, "h"), b"other", fetch).value, "token-2"
        )

    # === Rejected tokens === #

    @mute_logger(*LOGGERS)
    def test_revoked_token_is_renewed_and_request_replayed(self):
        tx = self._paid_tx()
        self.fake_payplug.revoke_tokens()
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "done")
        self.assertEqual(len(self._token_requests()), 2)
        first, second = self.fake_payplug.issued_tokens()
        # Creation, rejected reading, replayed reading.
        self.assertEqual(self._api_tokens(), [first, first, second])
        self.assertEqual(
            [request[1] for request in self._api_requests()[1:]],
            [f"/v1/payments/{tx.provider_reference}"] * 2,
        )

    @mute_logger(*LOGGERS)
    def test_request_replayed_only_once(self):
        self.fake_payplug.state.reject_all_tokens = True
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "error")
        self.assertEqual(len(self._token_requests()), 2)
        self.assertEqual(len(self._api_requests()), 2)
        self.assertFalse(self.fake_payplug.state.payments)

    @mute_logger(*LOGGERS)
    def test_api_key_errors_are_not_replayed(self):
        self.payplug.write(
            {"payplug_auth_method": "api_key", "payplug_secret_key": "sk_test_x"}
        )
        self.payplug.payplug_secret_key = "invalid-key"
        with self.assertRaises(ValidationError):
            self.payplug._send_api_request("GET", "payments/pay_unknown")
        self.assertEqual(len(self._api_requests()), 1)
        self.assertFalse(self._token_requests())

    # === Token endpoint errors === #

    @mute_logger(*LOGGERS)
    def test_invalid_credentials(self):
        wrong_secret = "fake_wrong_secret_8f3a"
        self.payplug.payplug_client_secret = wrong_secret
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "error")
        self.assertIn("client ID or secret", tx.state_message)
        self.assertNotIn(wrong_secret, tx.state_message)
        self.assertFalse(self._api_requests())
        self.assertFalse(oauth.TOKEN_CACHE.keys())
        # Nothing is cached after a failure: the next attempt asks again.
        with self.assertRaises(ValidationError):
            self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 2)

    @mute_logger(*LOGGERS)
    def test_token_endpoint_unavailable(self):
        self.fake_payplug.state.token_failure_status = 503
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "error")
        self.assertIn("unavailable (HTTP 503)", tx.state_message)
        self.assertFalse(self._api_requests())

    @mute_logger(*LOGGERS)
    def test_token_endpoint_timeout(self):
        with (
            patch(REQUESTS_POST, side_effect=requests.exceptions.Timeout),
            self.assertRaisesRegex(ValidationError, "Could not reach"),
        ):
            self.payplug._payplug_get_access_token()
        self.assertFalse(oauth.TOKEN_CACHE.keys())

    @mute_logger(*LOGGERS)
    def test_invalid_token_response(self):
        response = Mock(ok=True, status_code=200)
        for content in (
            {"token_type": "bearer", "expires_in": 299},
            {"access_token": "abc def", "token_type": "bearer"},
            {"access_token": "abc", "token_type": "mac"},
        ):
            response.json.return_value = content
            with (
                patch(REQUESTS_POST, return_value=response),
                self.assertRaisesRegex(ValidationError, "invalid access token"),
            ):
                self.payplug._payplug_get_access_token()
        response.json.side_effect = ValueError
        with (
            patch(REQUESTS_POST, return_value=response),
            self.assertRaisesRegex(ValidationError, "invalid access token"),
        ):
            self.payplug._payplug_get_access_token()

    def test_token_without_lifetime_is_not_reused(self):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {"access_token": "opaque", "scope": "test"}
        with patch(REQUESTS_POST, return_value=response) as post:
            self.assertEqual(self.payplug._payplug_get_access_token(), "opaque")
            self.payplug._payplug_get_access_token()
        self.assertEqual(post.call_count, 2)

    # === Environment (scope) === #

    @mute_logger(*LOGGERS)
    def test_live_key_refused_in_test_mode(self):
        self.payplug.write(
            {
                "payplug_client_id": LIVE_CLIENT_ID,
                "payplug_client_secret": LIVE_CLIENT_SECRET,
            }
        )
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "error")
        self.assertIn("Test environment", tx.state_message)
        self.assertFalse(self._api_requests())
        self.assertFalse(oauth.TOKEN_CACHE.keys())

    @mute_logger(*LOGGERS)
    def test_unknown_scope_refused_in_test_mode(self):
        self.fake_payplug.state.token_scope = "sandbox"
        with self.assertRaisesRegex(ValidationError, "scope: sandbox"):
            self.payplug._payplug_get_access_token()

    @mute_logger(*LOGGERS)
    def test_test_key_refused_when_enabled(self):
        self.payplug.state = "enabled"
        with self.assertRaisesRegex(ValidationError, "Live environment"):
            self.payplug._payplug_get_access_token()

    @mute_logger(*LOGGERS)
    def test_live_key_when_enabled(self):
        self.payplug.write(
            {
                "state": "enabled",
                "payplug_client_id": LIVE_CLIENT_ID,
                "payplug_client_secret": LIVE_CLIENT_SECRET,
            }
        )
        tx, _values = self._create_payplug_payment()
        self.assertTrue(tx.is_live)
        payment = self.fake_payplug.get_payment(tx.provider_reference)
        self.assertTrue(payment["is_live"])
        tx._payplug_fetch_and_process()
        self.assertEqual(tx.state, "pending")

    @mute_logger(*LOGGERS)
    def test_unknown_scope_accepted_when_enabled(self):
        # The scope of the Live tokens is not documented: an unknown one is accepted,
        # every payment being checked with `is_live`.
        self.fake_payplug.state.token_scope = "production"
        self.payplug.write(
            {
                "state": "enabled",
                "payplug_client_id": LIVE_CLIENT_ID,
                "payplug_client_secret": LIVE_CLIENT_SECRET,
            }
        )
        self.assertTrue(self.payplug._payplug_get_access_token())

    @mute_logger(*LOGGERS)
    def test_cached_token_checked_against_current_state(self):
        self.payplug._payplug_get_access_token()
        # As if another worker enabled the provider: this cache is not invalidated.
        with patch.object(oauth.TOKEN_CACHE, "invalidate"):
            self.payplug.state = "enabled"
        self.assertTrue(oauth.TOKEN_CACHE.keys())
        with self.assertRaisesRegex(ValidationError, "Live environment"):
            self.payplug._payplug_get_access_token()
        self.assertEqual(len(self._token_requests()), 1)

    def test_token_mode(self):
        self.assertEqual(oauth.get_token_mode({"test"}), oauth.MODE_TEST)
        self.assertEqual(oauth.get_token_mode({"live", "x"}), oauth.MODE_LIVE)
        self.assertEqual(oauth.get_token_mode({"test", "live"}), oauth.MODE_MIXED)
        self.assertEqual(oauth.get_token_mode(set()), oauth.MODE_UNKNOWN)
        token = self.payplug._payplug_get_access_token()
        self.assertEqual(oauth.get_token_scopes(token), {"test"})
        self.assertEqual(oauth.get_token_scopes("not-a-jwt", "a b"), {"a", "b"})
        self.assertEqual(oauth.decode_jwt_claims("a.%%%.c"), {})

    # === Configuration === #

    def test_credentials_required_by_method(self):
        with self.assertRaisesRegex(ValidationError, "must be filled"):
            self.payplug.payplug_client_secret = False
        with self.assertRaisesRegex(ValidationError, "must be filled"):
            self.payplug.payplug_auth_method = "api_key"  # No secret key.
        # A disabled provider needs no credentials.
        self.payplug.write({"state": "disabled", "payplug_client_id": False})
        self.payplug.write(
            {
                "state": "test",
                "payplug_auth_method": "api_key",
                "payplug_secret_key": TEST_SECRET_KEY,
            }
        )
        self.assertEqual(self.payplug.state, "test")

    def test_secret_key_prefix_not_checked_with_oauth2(self):
        # A legacy live key left in the field does not block the OAuth2 test mode.
        self.payplug.payplug_secret_key = "sk_live_whatever"
        self.assertEqual(self.payplug.state, "test")

    def test_client_secret_restricted_to_system_group(self):
        for field_name in ("payplug_client_id", "payplug_client_secret"):
            field = self.env["payment.provider"]._fields[field_name]
            self.assertEqual(field.groups, "base.group_system")
            with self.assertRaises(AccessError):
                self.payplug.with_user(self.internal_user).read([field_name])

    def test_reset_credentials_clears_oauth2_client(self):
        self.payplug.action_reset_credentials()
        self.assertFalse(self.payplug.payplug_client_id)
        self.assertFalse(self.payplug.payplug_client_secret)
        self.assertEqual(self.payplug.state, "disabled")

    @mute_logger(*LOGGERS)
    def test_api_key_method_still_works(self):
        self.payplug.write(
            {"payplug_auth_method": "api_key", "payplug_secret_key": TEST_SECRET_KEY}
        )
        tx, _values = self._create_payplug_payment()
        self.assertEqual(tx.state, "draft")
        self.assertEqual(self._api_tokens(), [TEST_SECRET_KEY])
        self.assertFalse(self._token_requests())

    # === Logs === #

    def test_no_secret_in_logs(self):
        with self.assertLogs(level="DEBUG") as logs:
            tx = self._paid_tx()
            tx._payplug_fetch_and_process()
            tx.action_refund(amount_to_refund=5.0)
            self.fake_payplug.revoke_tokens()
            tx._payplug_fetch_and_process()
        self.payplug.payplug_client_secret = "fake_wrong_secret_8f3a"
        with self.assertLogs(level="DEBUG") as error_logs:
            failed_tx, _values = self._create_payplug_payment(reference="failed-ref")
        self.assertEqual(tx.state, "done")
        self.assertEqual(failed_tx.state, "error")
        output = "\n".join(logs.output + error_logs.output)
        # The logs were captured: the requests and the token renewal are there.
        self.assertIn("Obtained a Payplug access token", output)
        self.assertIn("Payplug rejected the access token", output)
        self.assertIn("/v1/payments", output)
        tokens = self.fake_payplug.issued_tokens()
        self.assertEqual(len(tokens), 2)
        basic = base64.b64encode(
            f"{TEST_CLIENT_ID}:{TEST_CLIENT_SECRET}".encode()
        ).decode()
        for secret in (TEST_CLIENT_SECRET, "fake_wrong_secret_8f3a", basic, *tokens):
            self.assertNotIn(secret, output)
        for token in tokens:  # Not even the signature alone.
            self.assertNotIn(token.split(".")[2], output)
        self.assertNotIn("Bearer", output)
        self.assertNotIn("Basic", output)
