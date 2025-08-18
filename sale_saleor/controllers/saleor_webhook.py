# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import hmac
import json
import logging
from hashlib import sha256
from urllib.parse import urlparse

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


def _saleor_match_account(headers):
    """Match incoming webhook to an active Saleor account by exact origin.

    - Accept either Saleor-Domain or Saleor-Api-Url headers (including X- variants).
    - Normalize both header and account base_url to an origin string:
      scheme://host[:port] (no path, no trailing slash), lowercased.
    - Compare origins exactly; no fallback to the first active account.
    """
    Account = request.env["saleor.account"].sudo()

    header_val = (
        headers.get("Saleor-Domain")
        or headers.get("X-Saleor-Domain")
        or headers.get("Saleor-Api-Url")
        or headers.get("X-Saleor-Api-Url")
    )
    if not header_val:
        return None

    def to_origin(value: str) -> str:
        v = (value or "").strip()
        # If value lacks scheme, assume https for normalization
        if not v.lower().startswith(("http://", "https://")):
            v = "https://" + v
        try:
            p = urlparse(v)
            if not p.hostname:
                return ""
            scheme = (p.scheme or "https").lower()
            host = (p.hostname or "").lower()
            # Preserve explicit port if present and non-default for scheme
            port = p.port
            if port and not (
                (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
            ):
                netloc = f"{host}:{port}"
            else:
                netloc = host
            return f"{scheme}://{netloc}"
        except Exception:
            return ""

    hdr_origin = to_origin(header_val)
    if not hdr_origin:
        return None

    candidates = Account.search([("active", "=", True), ("base_url", "!=", False)])
    for acc in candidates:
        acc_origin = to_origin(acc.base_url)
        if acc_origin and acc_origin == hdr_origin:
            return acc
    return None


def _saleor_verify_signature(account, headers, body):
    secret_str = (account.saleor_webhook_secret or "").strip()
    if not secret_str:
        _logger.error(
            "Saleor webhook: secret not configured for account %s", account.id
        )
        resp = request.make_response(
            "secret not configured",
            headers=[("Content-Type", "text/plain")],
            status=500,
        )
        return False, resp

    secret = secret_str.encode("utf-8")
    sig_header = headers.get("Saleor-Signature") or headers.get("X-Saleor-Signature")
    if not sig_header:
        _logger.warning(
            "Saleor webhook: secret configured but signature header missing"
        )
        resp = request.make_response(
            "missing signature", headers=[("Content-Type", "text/plain")], status=401
        )
        return False, resp
    try:
        expected_hex = hmac.new(secret, body, sha256).hexdigest()
        # Some deployments prefix with algo, some do not; some may send base64
        sig_value = sig_header.strip()
        if "=" in sig_value:
            # e.g., sha256=<hex>
            sig_value = sig_value.split("=", 1)[-1].strip()
        valid = False
        # Try hex compare
        if hmac.compare_digest(expected_hex, sig_value):
            valid = True
        else:
            # Try base64
            try:
                import base64

                expected_b64 = base64.b64encode(bytes.fromhex(expected_hex)).decode(
                    "ascii"
                )
                if hmac.compare_digest(expected_b64, sig_value):
                    valid = True
            except Exception:
                valid = False
        if not valid:
            _logger.warning("Invalid Saleor webhook signature: %s", sig_header)
            resp = request.make_response(
                "bad signature", headers=[("Content-Type", "text/plain")], status=401
            )
            return False, resp
    except Exception as e:
        _logger.exception("Error verifying Saleor signature: %s", e)
        resp = request.make_response(
            "error", headers=[("Content-Type", "text/plain")], status=400
        )
        return False, resp
    return True, None


def _saleor_parse_payload(body, headers):
    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except Exception:
        payload = {}
    payload_event = payload.get("event") if isinstance(payload, dict) else None
    event_type_raw = (
        headers.get("Saleor-Event")
        or headers.get("X-Saleor-Event")
        or headers.get("Event-Type")
        or headers.get("X-Event-Type")
        or payload_event
    )
    event_type = (event_type_raw or "").upper()
    if isinstance(payload, list):
        data = payload
    elif isinstance(payload, dict):
        data = payload.get("payload") or payload.get("data") or {}
    else:
        data = {}
    return event_type, event_type_raw, data, payload


def _saleor_extract_order_id(data, payload):
    """Extract Saleor order ID from webhook payload data structures."""
    try:
        if isinstance(data, dict):
            return (data.get("order") or {}).get("id") or data.get("id")
        if isinstance(data, list) and data:
            first = data[0] or {}
            return (first.get("order") or {}).get("id") or first.get("id")
        if isinstance(payload, dict):
            return (payload.get("order") or {}).get("id") or payload.get("id")
    except Exception:
        return None
    return None


def _saleor_parse_order_payment_details(account, order_id, data):
    """Return (status, number, payment_dict) using payload first then API fallback."""

    def _first(lst):
        return (lst or [{}])[0] or {}

    status = None
    number = None
    pay = {}
    try:
        data_obj = None
        if isinstance(data, dict):
            data_obj = data
        elif isinstance(data, list) and data:
            data_obj = _first(data)
        if isinstance(data_obj, dict):
            status = data_obj.get("status") or status
            num_val = data_obj.get("number")
            if num_val is not None:
                number = str(num_val)
            pays = data_obj.get("payments") or []
            if isinstance(pays, list) and pays:
                pay = _first(pays)
    except Exception as pe:
        _logger.debug("Saleor webhook payload parse error: %s", pe)

    if not status or not number:
        try:
            client = account._get_client()
            account._refresh_token(client)
            api_order = client.order_get_by_id(order_id) or {}
            status = status or api_order.get("status")
            number = number or api_order.get("number")
        except Exception as e:
            _logger.debug("Saleor API fetch error for order %s: %s", order_id, e)
    return status, number, pay


def _saleor_build_payment_vals(so, status, number, pay, raw_body):
    """Build values dict to write on sale.order from parsed payment info."""
    vals = {}
    # Basic order vals
    vals.update(_saleor_basic_order_vals(so, status, number))
    # Payment fields
    vals.update(_saleor_payment_field_vals(so, pay))
    # Meta (payload, timestamp)
    vals.update(_saleor_payment_meta_vals(so, raw_body))
    return vals


def _saleor_basic_order_vals(so, status, number):
    vals = {}
    if hasattr(so, "saleor_mark_as_paid"):
        vals["saleor_mark_as_paid"] = True
    if hasattr(so, "saleor_status") and status:
        vals["saleor_status"] = status
    if hasattr(so, "saleor_number") and number is not None:
        vals["saleor_number"] = str(number)
    return vals


def _saleor_payment_field_vals(so, pay):
    vals = {}
    try:
        if isinstance(pay, dict) and pay:
            pid, gateway, cstatus, tot, cap, curr, psp = _saleor_extract_payment_fields(
                pay
            )
            if hasattr(so, "saleor_payment_id") and pid:
                vals["saleor_payment_id"] = pid
            if hasattr(so, "saleor_payment_gateway") and gateway:
                vals["saleor_payment_gateway"] = gateway
            if hasattr(so, "saleor_payment_charge_status") and cstatus:
                vals["saleor_payment_charge_status"] = cstatus
            if hasattr(so, "saleor_payment_total") and tot is not None:
                vals["saleor_payment_total"] = tot
            if hasattr(so, "saleor_payment_captured_amount") and cap is not None:
                vals["saleor_payment_captured_amount"] = cap
            if hasattr(so, "saleor_payment_currency") and curr:
                vals["saleor_payment_currency"] = curr
            if hasattr(so, "saleor_payment_psp_reference") and psp:
                vals["saleor_payment_psp_reference"] = psp
    except Exception as pe:
        _logger.debug("Saleor payment parse error: %s", pe)
    return vals


def _saleor_payment_meta_vals(so, raw_body):
    vals = {}
    try:
        if hasattr(so, "saleor_payment_payload") and raw_body:
            vals["saleor_payment_payload"] = raw_body
        if hasattr(so, "saleor_payment_updated"):
            vals["saleor_payment_updated"] = fields.Datetime.now()
    except Exception as te:
        _logger.debug("Saleor payment meta store error: %s", te)
    return vals


def _saleor_extract_payment_fields(pay):
    """Extract normalized payment fields from Saleor payment dict."""
    pid = pay.get("id")
    gateway = pay.get("gateway")
    cstatus = pay.get("charge_status")

    def _to_float(x):
        try:
            return float(x)
        except Exception:
            return None

    tot = _to_float(pay.get("total"))
    cap = _to_float(pay.get("captured_amount"))
    curr = pay.get("currency")
    psp = pay.get("psp_reference")
    return pid, gateway, cstatus, tot, cap, curr, psp


def _saleor_post_payment_message(so, status, number):
    try:
        msg = "Saleor payment update received"
        details = []
        if status:
            details.append(f"status: {status}")
        if number is not None:
            details.append(f"number: {number}")
        if details:
            msg = f"{msg} ({', '.join(details)})"
        so.message_post(body=msg)
    except Exception as me:
        _logger.debug(
            "Failed to post payment update chatter on sale.order %s: %s",
            so.id,
            me,
        )


def _saleor_extract_customer(data, payload, account):
    # Normalize data entry
    if isinstance(data, list):
        data_norm = data[0] if data else {}
    elif isinstance(data, dict):
        data_norm = data
    else:
        data_norm = {}
    # Determine id
    customer_id = (
        data_norm.get("id")
        or (data_norm.get("user") or {}).get("id")
        or (payload.get("id") if isinstance(payload, dict) else None)
    )
    if not customer_id:
        return None, None, None, None
    # Build from payload
    try:
        cust = {
            "id": customer_id,
            "email": data_norm.get("email") or data_norm.get("emailAddress"),
            "firstName": data_norm.get("first_name") or data_norm.get("firstName"),
            "lastName": data_norm.get("last_name") or data_norm.get("lastName"),
        }
        ship = (
            data_norm.get("default_shipping_address")
            or data_norm.get("defaultShippingAddress")
            or {}
        )
        bill = (
            data_norm.get("default_billing_address")
            or data_norm.get("defaultBillingAddress")
            or {}
        )
        cust["defaultShippingAddress"] = ship
        cust["defaultBillingAddress"] = bill
        if not cust.get("email") and account:
            client = account._get_client()
            api_cust = client.customer_get_by_id(customer_id) or {}
            if api_cust:
                cust = api_cust
                ship = cust.get("defaultShippingAddress") or {}
                bill = cust.get("defaultBillingAddress") or {}
    except Exception as e:
        _logger.exception("Saleor webhook: error normalizing payload: %s", e)
        cust, ship, bill = {}, {}, {}
    if not cust:
        return customer_id, None, None, None
    return customer_id, cust, ship, bill


def _resolve_country_state(a):
    Country = request.env["res.country"].sudo()
    State = request.env["res.country.state"].sudo()
    country_id = False
    state_id = False
    c = a.get("country")
    if c:
        dom = [
            "|",
            ("code", "=ilike", str(c).strip()),
            ("name", "=ilike", str(c).strip()),
        ]
        country = Country.search(dom, limit=1)
        if country:
            country_id = country.id
            s = a.get("state")
            if s:
                sdom = [
                    ("country_id", "=", country.id),
                    "|",
                    ("code", "=ilike", str(s).strip()),
                    ("name", "=ilike", str(s).strip()),
                ]
                state = State.search(sdom, limit=1)
                if state:
                    state_id = state.id
    return country_id, state_id


def _norm_addr(addr):
    if not isinstance(addr, dict):
        return {}
    return {
        "first_name": addr.get("first_name") or addr.get("firstName"),
        "last_name": addr.get("last_name") or addr.get("lastName"),
        "company_name": addr.get("company_name") or addr.get("companyName"),
        "street1": addr.get("street_address_1") or addr.get("streetAddress1"),
        "street2": addr.get("street_address_2") or addr.get("streetAddress2"),
        "city": addr.get("city"),
        "zip": addr.get("postal_code") or addr.get("postalCode"),
        "country": addr.get("country") or ((addr.get("countryInfo") or {}).get("code")),
        "state": addr.get("country_area") or addr.get("countryArea"),
        "phone": addr.get("phone") or addr.get("phoneNumber"),
    }


def _build_partner_vals(cust, shipping, billing):
    vals = {}
    email = cust.get("email")
    first = cust.get("firstName") or cust.get("first_name") or ""
    last = cust.get("lastName") or cust.get("last_name") or ""
    name = (first + " " + last).strip() or email
    if name:
        vals["name"] = name
    if email:
        vals["email"] = email
    phone = None
    if isinstance(shipping, dict):
        phone = shipping.get("phone") or shipping.get("phoneNumber")
    if not phone and isinstance(billing, dict):
        phone = billing.get("phone") or billing.get("phoneNumber")
    if phone:
        vals["phone"] = phone
    return vals


def _find_or_create_partner(account, customer_id, vals):
    Partner = request.env["res.partner"].sudo()
    partner = Partner.search(
        [
            ("saleor_customer_id", "=", customer_id),
            ("saleor_account_id", "=", account.id),
        ],
        limit=1,
    )
    if partner:
        partner.write(vals)
        return partner
    vals = dict(
        vals,
        saleor_customer_id=customer_id,
        saleor_account_id=account.id,
        type="contact",
        company_type="person",
    )
    return Partner.create(vals)


def _update_main_address(partner, shipping, billing):
    ship_norm = _norm_addr(shipping)
    bill_norm = _norm_addr(billing)
    main_addr = ship_norm or bill_norm
    if not main_addr:
        return
    addr_vals = {}
    if main_addr.get("street1"):
        addr_vals["street"] = main_addr.get("street1")
    if main_addr.get("street2"):
        addr_vals["street2"] = main_addr.get("street2")
    if main_addr.get("city"):
        addr_vals["city"] = main_addr.get("city")
    if main_addr.get("zip"):
        addr_vals["zip"] = main_addr.get("zip")
    c_id, s_id = _resolve_country_state(main_addr)
    if c_id:
        addr_vals["country_id"] = c_id
    if s_id:
        addr_vals["state_id"] = s_id
    if addr_vals:
        partner.write(addr_vals)


def _upsert_child_contact(partner, kind, data_norm):
    if not data_norm:
        return
    Partner = request.env["res.partner"].sudo()
    child = Partner.search(
        [
            ("parent_id", "=", partner.id),
            ("type", "=", kind),
        ],
        limit=1,
    )
    ch_vals = {}
    if data_norm.get("street1"):
        ch_vals["street"] = data_norm.get("street1")
    if data_norm.get("street2"):
        ch_vals["street2"] = data_norm.get("street2")
    if data_norm.get("city"):
        ch_vals["city"] = data_norm.get("city")
    if data_norm.get("zip"):
        ch_vals["zip"] = data_norm.get("zip")
    c_id, s_id = _resolve_country_state(data_norm)
    if c_id:
        ch_vals["country_id"] = c_id
    if s_id:
        ch_vals["state_id"] = s_id
    if data_norm.get("phone"):
        ch_vals["phone"] = data_norm.get("phone")
    name_parts = [
        p for p in [data_norm.get("first_name"), data_norm.get("last_name")] if p
    ]
    if name_parts:
        ch_vals["name"] = " ".join(name_parts)
    if data_norm.get("company_name"):
        ch_vals["company_name"] = data_norm.get("company_name")
    if not ch_vals:
        return
    if child:
        child.write(ch_vals)
    else:
        ch_vals.update({"type": kind, "parent_id": partner.id})
        Partner.create(ch_vals)


def _upsert_partner_and_addresses(account, customer_id, cust, ship, bill):
    shipping = (
        cust.get("defaultShippingAddress") or cust.get("default_shipping_address") or {}
    )
    billing = (
        cust.get("defaultBillingAddress") or cust.get("default_billing_address") or {}
    )
    vals = _build_partner_vals(cust, shipping, billing)
    _logger.info(
        "Saleor webhook: upserting partner for customer %s, vals=%s",
        customer_id,
        {k: vals[k] for k in vals.keys() if k in ("name", "email", "phone")},
    )
    partner = _find_or_create_partner(account, customer_id, vals)
    _update_main_address(partner, shipping, billing)
    _upsert_child_contact(partner, "delivery", _norm_addr(shipping))
    _upsert_child_contact(partner, "invoice", _norm_addr(billing))


class SaleorWebhookController(http.Controller):
    @http.route(
        "/saleor/webhook/order_created_updated",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def saleor_order_created_updated(self, **kwargs):  # pylint: disable=unused-argument
        body = request.httprequest.get_data() or b""
        headers = request.httprequest.headers
        account = _saleor_match_account(headers)
        if not account:
            _logger.warning("Saleor order webhook: no active account matched")
            return request.make_response(
                "no account", headers=[("Content-Type", "text/plain")], status=404
            )
        ok, resp = _saleor_verify_signature(account, headers, body)
        if not ok:
            return resp
        event_type, event_type_raw, data, payload = _saleor_parse_payload(body, headers)
        _logger.info(
            "Saleor order webhook: event=%s raw=%s", event_type, event_type_raw
        )

        if event_type not in {"ORDER_CREATED", "ORDER_UPDATED"}:
            return request.make_response(
                "ignored", headers=[("Content-Type", "text/plain")], status=200
            )

        # Extract order id and fetch full order from API
        order_id = _saleor_extract_order_id(data, payload)
        if not order_id:
            return request.make_response(
                "no id", headers=[("Content-Type", "text/plain")], status=200
            )
        try:
            client = account._get_client()
            order = client.order_get_by_id(order_id) or {}
        except Exception as e:
            _logger.exception(
                "Saleor order webhook: failed to fetch order %s: %s", order_id, e
            )
            return request.make_response(
                "error", headers=[("Content-Type", "text/plain")], status=500
            )

        # Skip orders that originated from Odoo (metadata/privateMetadata marker)
        try:
            pub_meta = {
                m.get("key"): m.get("value") for m in (order.get("metadata") or [])
            }
            priv_meta = {
                m.get("key"): m.get("value")
                for m in (order.get("privateMetadata") or [])
            }
            meta = {**pub_meta, **priv_meta}
            val = str(meta.get("odoo_origin", "")).strip().lower()
            if val in {"1", "true", "yes"}:
                _logger.info(
                    "Saleor order webhook: skipping Odoo-origin order %s", order_id
                )
                return request.make_response(
                    "skipped", headers=[("Content-Type", "text/plain")], status=200
                )
        except Exception as e:
            _logger.debug(
                "Saleor order webhook: error checking Odoo-origin flag: %s", e
            )

        # Upsert into Odoo
        try:
            account.sudo()._import_saleor_order(order)
            return request.make_response(
                "ok", headers=[("Content-Type", "text/plain")], status=200
            )
        except Exception as e:
            _logger.exception("Saleor order webhook: error upserting order: %s", e)
            return request.make_response(
                "error", headers=[("Content-Type", "text/plain")], status=500
            )

    @http.route(
        "/saleor/webhook/draft_order",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def saleor_draft_order_webhook(self, **kwargs):  # pylint: disable=unused-argument
        body = request.httprequest.get_data() or b""
        headers = request.httprequest.headers
        account = _saleor_match_account(headers)
        if not account:
            _logger.warning("Saleor draft order webhook: no active account matched")
            return request.make_response(
                "no account", headers=[("Content-Type", "text/plain")], status=404
            )
        ok, resp = _saleor_verify_signature(account, headers, body)
        if not ok:
            return resp
        event_type, event_type_raw, data, payload = _saleor_parse_payload(body, headers)
        _logger.info(
            "Saleor draft order webhook: event=%s raw=%s", event_type, event_type_raw
        )

        if event_type not in {"DRAFT_ORDER_CREATED", "DRAFT_ORDER_UPDATED"}:
            return request.make_response(
                "ignored", headers=[("Content-Type", "text/plain")], status=200
            )

        order_id = _saleor_extract_order_id(data, payload)
        if not order_id:
            return request.make_response(
                "no id", headers=[("Content-Type", "text/plain")], status=200
            )
        try:
            client = account._get_client()
            order = client.order_get_by_id(order_id) or {}
        except Exception as e:
            _logger.exception(
                "Saleor draft order webhook: failed to fetch order %s: %s", order_id, e
            )
            return request.make_response(
                "error", headers=[("Content-Type", "text/plain")], status=500
            )

        try:
            pub_meta = {
                m.get("key"): m.get("value") for m in (order.get("metadata") or [])
            }
            priv_meta = {
                m.get("key"): m.get("value")
                for m in (order.get("privateMetadata") or [])
            }
            meta = {**pub_meta, **priv_meta}
            val = str(meta.get("odoo_origin", "")).strip().lower()
            if val in {"1", "true", "yes"}:
                _logger.info(
                    "Saleor draft order webhook: skipping Odoo-origin order %s",
                    order_id,
                )
                return request.make_response(
                    "skipped",
                    headers=[("Content-Type", "text/plain")],
                    status=200,
                )
        except Exception as e:
            _logger.debug(
                "Saleor draft order webhook: error checking Odoo-origin flag: %s", e
            )

        try:
            account.sudo()._import_saleor_order(order)
            return request.make_response(
                "ok", headers=[("Content-Type", "text/plain")], status=200
            )
        except Exception as e:
            _logger.exception(
                "Saleor draft order webhook: error upserting order: %s", e
            )
            return request.make_response(
                "error", headers=[("Content-Type", "text/plain")], status=500
            )

    @http.route(
        "/saleor/webhook/customer",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def saleor_customer_webhook(self, **kwargs):  # pylint: disable=unused-argument
        # Read raw body for signature verification
        body = request.httprequest.get_data() or b""
        headers = request.httprequest.headers
        # Determine account
        account = _saleor_match_account(headers)
        if not account:
            _logger.warning("Saleor webhook: no matching or active account configured")
            return request.make_response(
                "no account", headers=[("Content-Type", "text/plain")], status=404
            )
        # Verify signature (warn on missing header if secret set)
        ok, resp = _saleor_verify_signature(account, headers, body)
        if not ok:
            return resp
        # Parse payload and event
        event_type, event_type_raw, data, payload = _saleor_parse_payload(body, headers)
        if event_type != "CUSTOMER_UPDATED":
            _logger.info("Saleor webhook: event ignored: %s", event_type_raw)
            return request.make_response(
                "ignored", headers=[("Content-Type", "text/plain")], status=200
            )
        # Extract customer and upsert
        customer_id, cust, shipping, billing = _saleor_extract_customer(
            data, payload, account
        )
        if not customer_id:
            _logger.warning(
                "Saleor customer webhook without id, payload type=%s",
                type(payload).__name__,
            )
            return request.make_response(
                "no id", headers=[("Content-Type", "text/plain")], status=200
            )
        if not cust:
            _logger.info("Saleor webhook: empty customer payload for %s", customer_id)
            return request.make_response(
                "empty", headers=[("Content-Type", "text/plain")], status=200
            )
        _upsert_partner_and_addresses(account, customer_id, cust, shipping, billing)

        # All good
        return request.make_response(
            "ok", headers=[("Content-Type", "text/plain")], status=200
        )

    @http.route(
        "/saleor/webhook/order_payment",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def saleor_order_payment_webhook(self, **kwargs):  # pylint: disable=unused-argument
        body = request.httprequest.get_data() or b""
        headers = request.httprequest.headers
        account = _saleor_match_account(headers)
        if not account:
            _logger.warning("Saleor order payment webhook: no active account matched")
            return request.make_response(
                "no account", headers=[("Content-Type", "text/plain")], status=404
            )
        ok, resp = _saleor_verify_signature(account, headers, body)
        if not ok:
            return resp
        event_type, event_type_raw, data, payload = _saleor_parse_payload(body, headers)
        _logger.info(
            "Saleor order payment webhook: event=%s raw=%s", event_type, event_type_raw
        )

        # Only process payment-related events
        if event_type not in {"ORDER_PAID", "ORDER_FULLY_PAID"}:
            return request.make_response(
                "ignored", headers=[("Content-Type", "text/plain")], status=200
            )

        # Extract order id
        order_id = _saleor_extract_order_id(data, payload)

        if not order_id:
            _logger.warning(
                "Saleor order payment webhook without order id, payload type=%s",
                type(payload).__name__,
            )
            return request.make_response(
                "no id", headers=[("Content-Type", "text/plain")], status=200
            )

        # Update corresponding sale.order
        try:
            SaleOrder = request.env["sale.order"].sudo()
            so = SaleOrder.search([("saleor_order_id", "=", order_id)], limit=1)
            if not so:
                _logger.info(
                    "Saleor order payment webhook: no sale.order linked to %s", order_id
                )
                return request.make_response(
                    "ok", headers=[("Content-Type", "text/plain")], status=200
                )

            status, number, pay = _saleor_parse_order_payment_details(
                account, order_id, data
            )
            raw = None
            try:
                raw = body.decode("utf-8")
            except Exception:
                raw = None
            vals = _saleor_build_payment_vals(so, status, number, pay, raw)
            if vals:
                try:
                    so.write(vals)
                except Exception as we:
                    _logger.warning(
                        "Failed to write payment flag on sale.order %s: %s", so.id, we
                    )
            _saleor_post_payment_message(so, status, number)
            return request.make_response(
                "ok", headers=[("Content-Type", "text/plain")], status=200
            )
        except Exception as e:
            _logger.exception("Error handling order payment webhook: %s", e)
            return request.make_response(
                "error", headers=[("Content-Type", "text/plain")], status=500
            )
