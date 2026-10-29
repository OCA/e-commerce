# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
"""Fake Payplug API server, for automated and manual tests only.

It imitates the subset of the Payplug REST API used by the module (creating, reading
and aborting a payment; creating and reading refunds), the OAuth2 token endpoint (client
credentials grant) and a minimal hosted payment page. It keeps everything in memory and
never contacts Payplug.

Standalone use, for a manual end-to-end test (point the system parameter
`payment_payplug.api_base_url` of the test database to http://<host>:<port>/v1/):

    python3 fake_payplug.py --host 0.0.0.0 --port 8765 --public-url http://<host>:8765

The API accepts any secret key starting with `sk_test_` or `sk_live_`, and the access
tokens issued by `POST /oauth2/token` to the fake OAuth2 clients below.
"""

import argparse
import base64
import binascii
import html
import json
import logging
import secrets
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

_logger = logging.getLogger(__name__)

API_VERSION = "2019-08-06"
TOKEN_AUDIENCE = "https://www.payplug.com"
TOKEN_LIFETIME = 299  # Seconds, like Payplug.

# Fake OAuth2 clients: client id -> (client secret, scope of their tokens).
OAUTH2_CLIENTS = {
    "fake_client_test": ("fake_client_secret_test", "test"),
    "fake_client_live": ("fake_client_secret_live", "live"),
}


def _b64url(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()


class FakePayplugError(Exception):
    def __init__(self, status, message, details=None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.details = details


class FakePayplugState:
    """In-memory state of the fake server."""

    def __init__(self):
        self.lock = threading.RLock()
        self.payments = {}
        self.refunds = {}
        self.requests = []  # (method, path, headers, body) of the API requests.
        self.notifications = []  # (url, body, status) of every notification sent.
        self.token_requests = []  # (headers, body) of the token requests.
        self.tokens = {}  # Access token -> {"scope", "expires_at", "revoked"}.
        self._reset_token_settings()

    def _reset_token_settings(self):
        self.token_lifetime = TOKEN_LIFETIME
        self.token_failure_status = None  # Force this status on the token endpoint.
        self.token_scope = None  # Override the scope of the issued tokens.
        self.reject_all_tokens = False  # Answer 401 to every access token.

    def reset(self):
        with self.lock:
            self.payments.clear()
            self.refunds.clear()
            self.requests.clear()
            self.notifications.clear()
            self.token_requests.clear()
            self.tokens.clear()
            self._reset_token_settings()


class FakePayplugServer:
    """A threaded HTTP server imitating the Payplug API."""

    def __init__(self, host="127.0.0.1", port=0, public_url=None, notify=False):
        self.state = FakePayplugState()
        self.notify = notify
        handler = type("BoundHandler", (FakePayplugHandler,), {"fake": self})
        self.httpd = ThreadingHTTPServer((host, port), handler)
        self.httpd.daemon_threads = True
        self.port = self.httpd.server_address[1]
        self.public_url = (public_url or f"http://{host}:{self.port}").rstrip("/")
        self.api_url = f"http://{host}:{self.port}/v1/"
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    # === State helpers (used by tests and by the hosted page) === #

    def get_payment(self, payment_id):
        return self.state.payments[payment_id]

    def mark_paid(self, payment_id, brand="Visa"):
        with self.state.lock:
            payment = self.state.payments[payment_id]
            payment.update(
                is_paid=True,
                paid_at=int(time.time()),
                card={"brand": brand, "last4": "4242", "country": "FR"},
            )
            payment["hosted_payment"]["paid_at"] = payment["paid_at"]
            return payment

    def mark_failed(
        self, payment_id, code="card_declined", message="The card was declined."
    ):
        with self.state.lock:
            payment = self.state.payments[payment_id]
            payment["failure"] = {"code": code, "message": message}
            return payment

    def create_refund(self, payment_id, amount=None, metadata=None):
        """Create a refund like the API (or the Payplug portal, without metadata)."""
        with self.state.lock:
            payment = self.state.payments[payment_id]
            if not payment["is_paid"]:
                raise FakePayplugError(400, "The payment is not paid.")
            remaining = payment["amount"] - payment["amount_refunded"]
            if amount is None:
                amount = remaining
            if not isinstance(amount, int) or amount < 10:
                raise FakePayplugError(
                    400, "Invalid amount.", {"amount": "minimum is 10"}
                )
            if amount > remaining:
                raise FakePayplugError(400, "The amount exceeds the refundable amount.")
            refund = {
                "id": f"re_{secrets.token_hex(10)}",
                "object": "refund",
                "payment_id": payment_id,
                "is_live": payment["is_live"],
                "amount": amount,
                "currency": payment["currency"],
                "created_at": int(time.time()),
                "metadata": metadata or {},
            }
            self.state.refunds[refund["id"]] = refund
            payment["amount_refunded"] += amount
            payment["is_refunded"] = payment["amount_refunded"] >= payment["amount"]
            return refund

    def issued_tokens(self):
        """Return the access tokens issued, in order."""
        return list(self.state.tokens)

    def revoke_tokens(self):
        """Revoke every access token issued: the API then answers 401 to them."""
        with self.state.lock:
            for token in self.state.tokens.values():
                token["revoked"] = True

    def issue_token(self, client_id, scope):
        """Issue an access token shaped like the Payplug ones (an unsigned JWT)."""
        issued_at = int(time.time())
        lifetime = self.state.token_lifetime
        claims = {
            "aud": [TOKEN_AUDIENCE],
            "client_id": client_id,
            "exp": issued_at + lifetime,
            "iat": issued_at,
            "jti": secrets.token_hex(8),
            "roles": ["plugin"],
            "scp": scope.split(),
        }
        header = {"alg": "RS256", "typ": "JWT"}
        token = ".".join((_b64url(header), _b64url(claims), secrets.token_urlsafe(32)))
        self.state.tokens[token] = {
            "scope": scope,
            "expires_at": issued_at + lifetime,
            "revoked": False,
        }
        return {
            "access_token": token,
            "expires_in": lifetime,
            "scope": scope,
            "token_type": "bearer",
        }

    def send_notification(self, obj):
        """POST the object to the notification URL of its payment, like Payplug does."""
        payment = self.state.payments[obj.get("payment_id") or obj["id"]]
        url = payment["notification"]["url"]
        if not url:
            return None
        body = json.dumps(obj).encode()
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        except OSError as error:
            _logger.warning("Notification to %s failed: %s", url, error)
            status = None
        payment["notification"]["response_code"] = status
        self.state.notifications.append((url, obj, status))
        return status


class FakePayplugHandler(BaseHTTPRequestHandler):
    fake = None  # Set on the bound subclass.

    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        _logger.debug("fake payplug: " + format, *args)

    # === Plumbing === #

    def _send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, error):
        data = {"object": "error", "message": error.message, "id": secrets.token_hex(8)}
        if error.details:
            data["details"] = error.details
        self._send_json(error.status, data)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        return raw

    def _authenticate(self):
        auth = self.headers.get("Authorization") or ""
        key = auth[len("Bearer ") :] if auth.startswith("Bearer ") else ""
        if key.startswith("sk_test_"):
            return False
        if key.startswith("sk_live_"):
            return True
        token = self.fake.state.tokens.get(key)
        if (
            token
            and not token["revoked"]
            and not self.fake.state.reject_all_tokens
            and time.time() < token["expires_at"]
        ):
            return "live" in token["scope"].split()
        raise FakePayplugError(401, "Invalid API key.")

    # === OAuth2 token endpoint === #

    def _send_oauth2_error(self, status, error, description):
        self._send_json(status, {"error": error, "error_description": description})

    def _token(self, method, raw):
        """POST /oauth2/token: the client credentials grant, client_secret_basic."""
        state = self.fake.state
        state.token_requests.append((dict(self.headers), raw))
        if method != "POST":
            return self._send_oauth2_error(405, "invalid_request", "POST only.")
        if state.token_failure_status:
            return self._send_json(
                state.token_failure_status, {"error": "server_error"}
            )
        content_type = (self.headers.get("Content-Type") or "").split(";")[0]
        if content_type != "application/x-www-form-urlencoded":
            return self._send_oauth2_error(400, "invalid_request", "Form body only.")
        body = {key: values[0] for key, values in parse_qs(raw.decode()).items()}
        if "client_secret" in body or "client_id" in body:
            return self._send_oauth2_error(
                400, "invalid_request", "Use client_secret_basic."
            )
        auth = self.headers.get("Authorization") or ""
        try:
            decoded = base64.b64decode(auth[len("Basic ") :], validate=True).decode()
        except (binascii.Error, UnicodeDecodeError):
            decoded = ""
        client_id, _sep, client_secret = decoded.partition(":")
        client = OAUTH2_CLIENTS.get(client_id)
        if (
            not auth.startswith("Basic ")
            or not client
            or not secrets.compare_digest(client[0], client_secret)
        ):
            return self._send_oauth2_error(
                401, "invalid_client", "Client authentication failed."
            )
        if body.get("grant_type") != "client_credentials":
            return self._send_oauth2_error(
                400, "unsupported_grant_type", "Unsupported grant type."
            )
        if body.get("audience") != TOKEN_AUDIENCE:
            return self._send_oauth2_error(400, "invalid_request", "Invalid audience.")
        with state.lock:
            data = self.fake.issue_token(client_id, state.token_scope or client[1])
        return self._send_json(200, data)

    def _get_payment(self, payment_id, is_live):
        payment = self.fake.state.payments.get(payment_id)
        if not payment or payment["is_live"] != is_live:
            raise FakePayplugError(
                404, "The resource you requested could not be found."
            )
        return payment

    def do_GET(self):  # noqa: N802
        self._dispatch("GET")

    def do_POST(self):  # noqa: N802
        self._dispatch("POST")

    def do_PATCH(self):  # noqa: N802
        self._dispatch("PATCH")

    def _dispatch(self, method):
        path = urlsplit(self.path).path.rstrip("/")
        parts = [p for p in path.split("/") if p]
        raw = self._read_body()
        try:
            if parts[:1] == ["pay"]:
                return self._hosted_page(method, parts, raw)
            if parts[:1] == ["_control"]:
                return self._control(method, parts, raw)
            if parts == ["oauth2", "token"]:
                return self._token(method, raw)
            if parts[:1] != ["v1"]:
                raise FakePayplugError(404, "Not found.")
            self.fake.state.requests.append((method, path, dict(self.headers), raw))
            if self.headers.get("PayPlug-Version") != API_VERSION:
                raise FakePayplugError(
                    400, "Missing or unexpected PayPlug-Version header."
                )
            is_live = self._authenticate()
            body = json.loads(raw) if raw else {}
            with self.fake.state.lock:
                status, data = self._api(method, parts[1:], body, is_live)
            self._send_json(status, data)
        except FakePayplugError as error:
            self._send_error(error)
        except (ValueError, KeyError, TypeError) as error:
            self._send_error(FakePayplugError(400, f"Bad request: {error}"))

    # === API === #

    def _api(self, method, parts, body, is_live):
        if parts == ["payments"] and method == "POST":
            return 201, self._create_payment(body, is_live)
        if len(parts) == 2 and parts[0] == "payments":
            payment = self._get_payment(parts[1], is_live)
            if method == "GET":
                return 200, payment
            if method == "PATCH":
                if body.get("aborted"):
                    if payment["is_paid"] or payment["failure"]:
                        raise FakePayplugError(400, "The payment cannot be aborted.")
                    payment["failure"] = {
                        "code": "aborted",
                        "message": "Payment aborted.",
                    }
                    return 200, payment
        if len(parts) == 3 and parts[0] == "payments" and parts[2] == "refunds":
            payment = self._get_payment(parts[1], is_live)
            if method == "POST":
                refund = self.fake.create_refund(
                    payment["id"], body.get("amount"), body.get("metadata")
                )
                if self.fake.notify:
                    notification = {
                        key: refund[key] for key in ("id", "object", "payment_id")
                    }
                    threading.Timer(
                        1.0, self.fake.send_notification, [notification]
                    ).start()
                return 201, refund
            if method == "GET":
                refunds = [
                    r
                    for r in self.fake.state.refunds.values()
                    if r["payment_id"] == parts[1]
                ]
                return 200, {"object": "list", "data": refunds}
        if len(parts) == 4 and parts[0] == "payments" and parts[2] == "refunds":
            self._get_payment(parts[1], is_live)
            refund = self.fake.state.refunds.get(parts[3])
            if method == "GET" and refund and refund["payment_id"] == parts[1]:
                return 200, refund
            raise FakePayplugError(
                404, "The resource you requested could not be found."
            )
        raise FakePayplugError(404, "Not found.")

    def _create_payment(self, body, is_live):
        amount = body.get("amount")
        details = {}
        if body.get("currency") != "EUR":
            details["currency"] = "Only EUR is supported."
        if not isinstance(amount, int) or not 30 <= amount <= 2000000:
            details["amount"] = "The amount must be an integer between 30 and 2000000."
        for key in ("billing", "shipping"):
            if not isinstance(body.get(key), dict):
                details[key] = "This field is required."
        hosted = body.get("hosted_payment") or {}
        for key in ("return_url", "cancel_url"):
            if hosted.get(key) and not hosted[key].startswith(("http://", "https://")):
                details[f"hosted_payment.{key}"] = "Invalid URL."
        if len(json.dumps(body.get("metadata") or {})) > 1000:
            details["metadata"] = "Too long."
        if len(body.get("description") or "") > 80:
            details["description"] = "Too long."
        if details:
            raise FakePayplugError(400, "Invalid parameters.", details)
        payment_id = f"pay_{secrets.token_hex(10)}"
        mode = "live" if is_live else "test"
        payment = {
            "id": payment_id,
            "object": "payment",
            "is_live": is_live,
            "amount": amount,
            "amount_refunded": 0,
            "authorization": None,
            "currency": "EUR",
            "created_at": int(time.time()),
            "description": body.get("description"),
            "is_paid": False,
            "paid_at": None,
            "is_refunded": False,
            "is_3ds": None,
            "save_card": False,
            "card": {"last4": None, "country": None, "exp_year": None, "brand": None},
            "billing": body.get("billing"),
            "shipping": body.get("shipping"),
            "payment_method": body.get("payment_method"),
            "hosted_payment": {
                "payment_url": f"{self.fake.public_url}/pay/{mode}/{payment_id}",
                "return_url": hosted.get("return_url"),
                "cancel_url": hosted.get("cancel_url"),
                "paid_at": None,
                "sent_by": None,
            },
            "notification": {
                "url": body.get("notification_url"),
                "response_code": None,
            },
            "failure": None,
            "metadata": body.get("metadata") or {},
        }
        self.fake.state.payments[payment_id] = payment
        return payment

    # === Control routes (manual tests) === #

    def _control(self, method, parts, raw):
        """POST /_control/refund/<payment_id> {"amount": cents}: portal refund."""
        if method != "POST" or len(parts) != 3 or parts[1] != "refund":
            raise FakePayplugError(404, "Not found.")
        body = json.loads(raw) if raw else {}
        refund = self.fake.create_refund(parts[2], body.get("amount"))
        status = self.fake.send_notification(
            {key: refund[key] for key in ("id", "object", "payment_id")}
        )
        self._send_json(201, dict(refund, notification_status=status))

    # === Hosted payment page (manual tests) === #

    def _hosted_page(self, method, parts, raw):
        # /pay/<mode>/<payment_id>
        payment = self.fake.state.payments.get(parts[2]) if len(parts) == 3 else None
        if not payment:
            raise FakePayplugError(404, "Unknown payment.")
        if method == "GET":
            amount = f"{payment['amount'] / 100:.2f} EUR"
            title = html.escape(str(payment["description"]))
            page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Faux Payplug</title></head>
<body style="font-family:sans-serif;max-width:30em;margin:3em auto">
<h1>Faux Payplug (test)</h1><p>Paiement <b>{title}</b> : <b>{amount}</b></p>
<form method="post"><button name="action" value="pay">Payer</button>
<button name="action" value="refuse">Refuser (carte refusée)</button>
<button name="action" value="cancel">Annuler</button></form></body></html>"""
            body = page.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return None
        action = parse_qs(raw.decode()).get("action", [""])[0]
        target = payment["hosted_payment"]["return_url"]
        if action == "pay":
            self.fake.mark_paid(payment["id"])
        elif action == "refuse":
            self.fake.mark_failed(payment["id"])
        else:
            target = payment["hosted_payment"]["cancel_url"]
        if action in ("pay", "refuse") and self.fake.notify:
            self.fake.send_notification(
                {
                    "id": payment["id"],
                    "object": "payment",
                    "is_live": payment["is_live"],
                }
            )
        self.send_response(303)
        self.send_header("Location", target)
        self.end_headers()
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--public-url", help="URL of the hosted pages seen by the browser"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    server = FakePayplugServer(args.host, args.port, args.public_url, notify=True)
    _logger.info(
        "Fake Payplug API on %s (pages on %s)", server.api_url, server.public_url
    )
    try:
        server.httpd.serve_forever()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()
