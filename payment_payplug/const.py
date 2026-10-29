# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

# Base URL of the Payplug REST API. The system parameter below overrides it; it is only
# meant for tests (e.g. a local fake server). The same endpoints serve the live and test
# modes, the secret key alone selecting the mode.
# See https://docs.payplug.com/api/apiref.html
DEFAULT_API_BASE_URL = "https://api.payplug.com/v1/"
API_BASE_URL_PARAM = "payment_payplug.api_base_url"

# OAuth2 client credentials grant. By default, the token endpoint is `/oauth2/token` on
# the host of the API. The system parameters below override the endpoint and the
# audience; like the base URL, they are only meant for tests.
TOKEN_PATH = "/oauth2/token"
TOKEN_URL_PARAM = "payment_payplug.token_url"
DEFAULT_TOKEN_AUDIENCE = "https://www.payplug.com"
TOKEN_AUDIENCE_PARAM = "payment_payplug.token_audience"
# Seconds before the expiry of an access token at which it is renewed.
TOKEN_RENEWAL_MARGIN = 60
# Timeout of the token requests, in seconds (the same as the API requests).
TOKEN_REQUEST_TIMEOUT = 10

# Version of the API used by this module, sent in the `PayPlug-Version` header.
API_VERSION = "2019-08-06"

# Prefixes of the secret keys depending on the environment.
SECRET_KEY_PREFIX_TEST = "sk_test_"
SECRET_KEY_PREFIX_LIVE = "sk_live_"

# Payplug only processes payments in euros.
SUPPORTED_CURRENCIES = ("EUR",)

# Amount limits in minor units (cents), from the API reference.
MINIMUM_PAYMENT_AMOUNT = 30
MAXIMUM_PAYMENT_AMOUNT = 2000000
MINIMUM_REFUND_AMOUNT = 10

# The codes of the payment methods to activate when Payplug is activated.
DEFAULT_PAYMENT_METHOD_CODES = {
    # Primary payment methods.
    "card",
    # Brand payment methods.
    "visa",
    "mastercard",
    "cartes_bancaires",
}

# Mapping of Odoo payment method codes to the `payment_method` values of the Payplug
# API. The `card` method is the default one of the hosted payment page: it is not sent.
PAYMENT_METHODS_MAPPING = {
    "bancontact": "bancontact",
    "ideal": "ideal",
    "mybank": "mybank",
}

# Mapping of card brands returned by Payplug (lowercased) to Odoo payment method codes.
CARD_BRANDS_MAPPING = {
    "visa": "visa",
    "mastercard": "mastercard",
    "cb": "cartes_bancaires",
    "maestro": "maestro",
}

# Languages supported by the hosted payment page (ISO 639-1).
SUPPORTED_LANGUAGES = ("fr", "en", "it")
DEFAULT_LANGUAGE = "en"

# Failure codes after which the payment is considered as canceled rather than failed.
CANCEL_FAILURE_CODES = ("aborted", "timeout")

# Maximum lengths of the billing and shipping fields.
FIELD_MAX_LENGTHS = {
    "first_name": 100,
    "last_name": 100,
    "email": 255,
    "address1": 255,
    "address2": 255,
    "postcode": 16,
    "city": 100,
    "company_name": 100,
}
DESCRIPTION_MAX_LENGTH = 80

# Keys of the payment data that must never be logged.
SENSITIVE_KEYS = {
    "secret_key",
    "Authorization",
    "client_secret",
    "access_token",
    "payplug_secret_key",
    "payplug_client_secret",
}
