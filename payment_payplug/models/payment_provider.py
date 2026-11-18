# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import re
import threading
from urllib.parse import urlsplit, urlunsplit

import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import urls

from odoo.addons.payment.logging import get_payment_logger

from .. import const, oauth

_logger = get_payment_logger(__name__, sensitive_keys=const.SENSITIVE_KEYS)

# The fields whose change makes the cached access tokens of a provider obsolete.
OAUTH2_FIELDS = {
    "state",
    "payplug_auth_method",
    "payplug_client_id",
    "payplug_client_secret",
}

# Status code of the last API error response, per thread: the payment framework turns
# the HTTP errors into `ValidationError`, without their status code.
_last_api_error = threading.local()

OAUTH2_ERROR_CODE_RE = re.compile(r"^[a-z_]{1,64}$")


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("payplug", "Payplug")],
        ondelete={"payplug": "set default"},
    )
    payplug_auth_method = fields.Selection(
        string="Payplug Authentication",
        selection=[("api_key", "API Key"), ("oauth2", "OAuth2")],
        default="api_key",
        help="API Key: the secret key of your Payplug account is sent with every "
        "request.\n"
        "OAuth2: Odoo exchanges a client ID and secret for access tokens valid a few "
        "minutes, renewed automatically.",
    )
    payplug_secret_key = fields.Char(
        help="The secret key of your Payplug account: a key of the Test environment "
        "in test mode, a key of the Live environment when the provider is enabled.",
        copy=False,
        groups="base.group_system",
    )
    payplug_client_id = fields.Char(
        string="Payplug Client ID",
        help="The client ID of an OAuth2 key of your Payplug account: a key of the "
        "Test environment in test mode, a key of the Live environment when the "
        "provider is enabled.",
        copy=False,
        groups="base.group_system",
    )
    payplug_client_secret = fields.Char(
        help="The client secret of the OAuth2 key, shown once by the Payplug portal "
        "when the key is created.",
        copy=False,
        groups="base.group_system",
    )

    # === COMPUTE METHODS === #

    def _compute_feature_support_fields(self):
        """Override of `payment` to enable additional features."""
        res = super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == "payplug").update(
            {
                "support_refund": "partial",
            }
        )
        return res

    def _get_supported_currencies(self):
        """Override of `payment` to return the supported currencies."""
        supported_currencies = super()._get_supported_currencies()
        if self.code == "payplug":
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies

    # === CONSTRAINT METHODS === #

    @api.constrains("state", "payplug_auth_method", "payplug_secret_key")
    def _check_payplug_secret_key_matches_state(self):
        """Prevent using a live key in test mode, and a test key on an enabled provider.

        Payplug serves both modes on the same endpoints; the key alone decides whether
        real money is charged. A mismatch would either charge customers during tests or
        accept fake payments in production.
        """
        for provider in self.sudo().filtered(
            lambda p: p.code == "payplug"
            and p.state != "disabled"
            and p.payplug_auth_method != "oauth2"
            and p.payplug_secret_key
        ):
            key = provider.payplug_secret_key.strip()
            if not key.startswith("sk_"):
                # Keys issued by the current Payplug portal are JWTs without a mode
                # prefix; the mode is then checked on every payment (`is_live`).
                continue
            if provider.state == "test" and not key.startswith(
                const.SECRET_KEY_PREFIX_TEST
            ):
                raise ValidationError(
                    self.env._(
                        "In test mode, the Payplug secret key must be a test key "
                        "(starting with %s).",
                        const.SECRET_KEY_PREFIX_TEST,
                    )
                )
            if provider.state == "enabled" and not key.startswith(
                const.SECRET_KEY_PREFIX_LIVE
            ):
                raise ValidationError(
                    self.env._(
                        "When the provider is enabled, the Payplug secret key must be "
                        "a live key (starting with %s).",
                        const.SECRET_KEY_PREFIX_LIVE,
                    )
                )

    def _check_required_if_provider(self):
        """Override of `payment` to require the credentials of the chosen method.

        The secret key is required with the API key method only, the client ID and
        secret with the OAuth2 method only.
        """
        res = super()._check_required_if_provider()
        missing_fields = set()
        for provider in self.sudo().filtered(
            lambda p: p.code == "payplug" and p.state in ("enabled", "test")
        ):
            if provider.payplug_auth_method == "oauth2":
                required_fields = ("payplug_client_id", "payplug_client_secret")
            else:
                required_fields = ("payplug_secret_key",)
            missing_fields.update(
                field for field in required_fields if not provider[field]
            )
        if missing_fields:
            field_names = [
                self.env["ir.model.fields"]._get(self._name, field).field_description
                for field in sorted(missing_fields)
            ]
            raise ValidationError(
                self.env._(
                    "The following fields must be filled: %s", ", ".join(field_names)
                )
            )
        return res

    # === CRUD METHODS === #

    def write(self, vals):
        """Override of `payment` to forget the access tokens of changed credentials."""
        res = super().write(vals)
        if OAUTH2_FIELDS.intersection(vals):
            for provider in self.filtered(lambda p: p.code == "payplug"):
                oauth.TOKEN_CACHE.invalidate(self.env.cr.dbname, provider.id)
        return res

    def _get_default_payment_method_codes(self):
        """Override of `payment` to return the default payment method codes."""
        self.ensure_one()
        if self.code != "payplug":
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _get_reset_values(self):
        """Override of `payment` to also reset the secret key and OAuth2 client."""
        values = super()._get_reset_values()
        if self.code == "payplug":
            values.update(
                payplug_secret_key=False,
                payplug_client_id=False,
                payplug_client_secret=False,
            )
        return values

    # === REQUEST HELPERS === #

    def _payplug_get_api_base_url(self):
        """Return the base URL of the Payplug API, ending with a slash.

        The URL can be overridden with a system parameter so that tests target a local
        fake server instead of the real API.
        """
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param(const.API_BASE_URL_PARAM)
            or const.DEFAULT_API_BASE_URL
        )
        return base_url.rstrip("/") + "/"

    def _payplug_get_token_url(self):
        """Return the URL of the OAuth2 token endpoint.

        By default, `/oauth2/token` on the host of the API; a system parameter overrides
        it for tests.
        """
        token_url = (
            self.env["ir.config_parameter"].sudo().get_param(const.TOKEN_URL_PARAM)
        )
        if token_url:
            return token_url
        split_url = urlsplit(self._payplug_get_api_base_url())
        return urlunsplit(
            (split_url.scheme, split_url.netloc, const.TOKEN_PATH, "", "")
        )

    def _payplug_get_token_audience(self):
        """Return the audience requested for the OAuth2 access tokens."""
        return (
            self.env["ir.config_parameter"].sudo().get_param(const.TOKEN_AUDIENCE_PARAM)
            or const.DEFAULT_TOKEN_AUDIENCE
        )

    def _payplug_get_authorization_header(self):
        """Return the value of the `Authorization` header of the API requests.

        With the API key method, the secret key; with the OAuth2 method, a valid access
        token, requested or renewed when needed.

        Note: self.ensure_one()

        :return: The header value.
        :rtype: str
        :raise ValidationError: If no access token can be obtained.
        """
        self.ensure_one()
        if self.payplug_auth_method == "oauth2":
            return f"Bearer {self._payplug_get_access_token()}"
        secret_key = (self.sudo().payplug_secret_key or "").strip()
        return f"Bearer {secret_key}"

    def _payplug_get_access_token(self):
        """Return a valid OAuth2 access token, from the cache or a new one.

        Note: self.ensure_one()

        :return: The access token.
        :rtype: str
        :raise ValidationError: If the credentials are missing, if the token endpoint
            fails, or if the environment of the token does not match the provider.
        """
        self.ensure_one()
        client_id = (self.sudo().payplug_client_id or "").strip()
        client_secret = (self.sudo().payplug_client_secret or "").strip()
        if not client_id or not client_secret:
            raise ValidationError(
                self.env._("The Payplug OAuth2 client ID and secret are not set.")
            )
        token_url = self._payplug_get_token_url()
        audience = self._payplug_get_token_audience()
        key = oauth.make_cache_key(
            self.env.cr.dbname, self.id, client_id, token_url, audience
        )

        def fetch():
            value, expires_in, mode, scope = self._payplug_request_access_token(
                client_id, client_secret, token_url, audience
            )
            # Never cache a token of the wrong environment.
            self._payplug_check_token_mode(mode, scope)
            return value, expires_in, mode, scope

        token = oauth.TOKEN_CACHE.get_or_fetch(
            key, oauth.TOKEN_CACHE.fingerprint(client_secret), fetch
        )
        # The state of the provider may have changed since the token was cached.
        self._payplug_check_token_mode(token.mode, token.scope)
        return token.value

    def _payplug_invalidate_access_token(self):
        """Forget the cached access tokens of the provider."""
        for provider in self:
            oauth.TOKEN_CACHE.invalidate(self.env.cr.dbname, provider.id)

    def _payplug_request_access_token(
        self, client_id, client_secret, token_url, audience
    ):
        """Request an access token with the OAuth2 client credentials grant.

        The client authenticates with HTTP Basic (`client_secret_basic`). Neither the
        credentials nor the token are ever logged; the response body is not logged
        either, as it holds the token.

        :param str client_id: The OAuth2 client ID.
        :param str client_secret: The OAuth2 client secret.
        :param str token_url: The URL of the token endpoint.
        :param str audience: The requested audience.
        :return: The token, its lifetime in seconds, its environment and its scope.
        :rtype: tuple
        :raise ValidationError: If the request fails.
        """
        _logger.info("Requesting a Payplug access token for provider %s.", self.id)
        try:
            response = requests.post(
                token_url,
                data={"grant_type": "client_credentials", "audience": audience},
                auth=(client_id.encode(), client_secret.encode()),
                headers={"Accept": "application/json"},
                timeout=const.TOKEN_REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        except requests.exceptions.RequestException as error:
            _logger.warning(
                "Payplug token request of provider %s failed: %s",
                self.id,
                type(error).__name__,
            )
            raise ValidationError(
                self.env._(
                    "Could not reach the Payplug authorization server to get an access "
                    "token. Please try again later."
                )
            ) from None

        try:
            content = response.json()
        except ValueError:
            content = None
        if not isinstance(content, dict):
            content = {}

        if not response.ok:
            error_code = content.get("error")
            if not isinstance(error_code, str) or not OAUTH2_ERROR_CODE_RE.match(
                error_code
            ):
                error_code = ""
            _logger.warning(
                "Payplug refused the token request of provider %s: HTTP %s %s",
                self.id,
                response.status_code,
                error_code,
            )
            if response.status_code == 401 or error_code in (
                "invalid_client",
                "unauthorized_client",
            ):
                message = self.env._(
                    "Payplug refused the OAuth2 client ID or secret. Check them, and "
                    "check that the key belongs to the right environment (Test or "
                    "Live)."
                )
            elif response.status_code >= 500:
                message = self.env._(
                    "The Payplug authorization server is unavailable (HTTP %s). Please "
                    "try again later.",
                    response.status_code,
                )
            else:
                message = self.env._(
                    "Payplug refused the access token request (HTTP %(status)s "
                    "%(error)s).",
                    status=response.status_code,
                    error=error_code,
                )
            raise ValidationError(message)

        value = content.get("access_token")
        token_type = content.get("token_type")
        if (
            not isinstance(value, str)
            or not value
            or any(char.isspace() for char in value)
            or (isinstance(token_type, str) and token_type.lower() != "bearer")
        ):
            _logger.warning(
                "Invalid Payplug token response for provider %s (HTTP %s).",
                self.id,
                response.status_code,
            )
            raise ValidationError(
                self.env._("Payplug returned an invalid access token response.")
            )

        expires_in = content.get("expires_in")
        if not isinstance(expires_in, (int, float)) or isinstance(expires_in, bool):
            # Fall back on the lifetime stated in the token; without any, the token is
            # used for this request only.
            claims = oauth.decode_jwt_claims(value)
            exp, iat = claims.get("exp"), claims.get("iat")
            expires_in = (
                exp - iat if isinstance(exp, int) and isinstance(iat, int) else 0
            )
        expires_in = max(int(expires_in), 0)
        scope = content.get("scope")
        scopes = oauth.get_token_scopes(value, scope)
        _logger.info(
            "Obtained a Payplug access token for provider %s (scope: %s, valid for %s "
            "seconds).",
            self.id,
            " ".join(sorted(scopes)) or "-",
            expires_in,
        )
        return value, expires_in, oauth.get_token_mode(scopes), " ".join(sorted(scopes))

    def _payplug_check_token_mode(self, mode, scope):
        """Check that the environment of an access token matches the provider state.

        In test mode, the token must be explicitly of the Test environment. When the
        provider is enabled, a token of the Test environment is refused; a token whose
        environment is not stated is accepted, the environment of every payment being
        checked anyway (`is_live`).

        :param str mode: The environment of the token, see `oauth.get_token_mode`.
        :param str scope: The scopes of the token, for the error message.
        :raise ValidationError: If the environment does not match.
        """
        if self.state == "test" and mode != oauth.MODE_TEST:
            raise ValidationError(
                self.env._(
                    "In test mode, the Payplug OAuth2 key must be a key of the Test "
                    "environment (access token scope: %s).",
                    scope or "-",
                )
            )
        if self.state == "enabled" and mode in (oauth.MODE_TEST, oauth.MODE_MIXED):
            raise ValidationError(
                self.env._(
                    "When the provider is enabled, the Payplug OAuth2 key must be a "
                    "key of the Live environment (access token scope: %s).",
                    scope or "-",
                )
            )

    def _send_api_request(self, method, endpoint, **kwargs):
        """Override of `payment` to renew a rejected OAuth2 access token once.

        When the API answers 401 to a request sent with an access token, the token may
        have been revoked or have expired early: it is forgotten, a new one is requested
        and the request is sent again, once. An unauthenticated request has no effect on
        Payplug, so it can safely be sent again.
        """
        if self.code != "payplug" or self.payplug_auth_method != "oauth2":
            return super()._send_api_request(method, endpoint, **kwargs)
        _last_api_error.status_code = None
        try:
            return super()._send_api_request(method, endpoint, **kwargs)
        except ValidationError:
            if _last_api_error.status_code != 401:
                raise
        _logger.info(
            "Payplug rejected the access token of provider %s; requesting a new one.",
            self.id,
        )
        self._payplug_invalidate_access_token()
        return super()._send_api_request(method, endpoint, **kwargs)

    def _build_request_url(self, endpoint, **kwargs):
        """Override of `payment` to build the request URL."""
        if self.code != "payplug":
            return super()._build_request_url(endpoint, **kwargs)
        return urls.urljoin(self._payplug_get_api_base_url(), endpoint.strip("/"))

    def _build_request_headers(self, method, endpoint, payload, **kwargs):
        """Override of `payment` to build the request headers."""
        if self.code != "payplug":
            return super()._build_request_headers(method, endpoint, payload, **kwargs)
        return {
            "Accept": "application/json",
            "Authorization": self._payplug_get_authorization_header(),
            "Content-Type": "application/json",
            "PayPlug-Version": const.API_VERSION,
        }

    def _parse_response_error(self, response):
        """Override of `payment` to parse the error message."""
        if self.code != "payplug":
            return super()._parse_response_error(response)
        _last_api_error.status_code = response.status_code
        try:
            content = response.json()
        except ValueError:
            content = None
        if not isinstance(content, dict):
            return response.text
        message = content.get("message") or response.text
        details = content.get("details")
        if details:
            message = f"{message} {details}"
        return message
