# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
"""In-process cache of the Payplug OAuth2 access tokens, and token helpers.

The access tokens obtained with the client credentials grant live a few minutes. They
are kept in the memory of the process only (never in the database), keyed by database,
provider and a hash of the client id and token endpoint; the client secret is never part
of the key. Each Odoo worker process thus requests its own tokens.
"""

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import threading
import time
from collections import namedtuple

from . import const

MODE_TEST = "test"
MODE_LIVE = "live"
MODE_UNKNOWN = "unknown"
MODE_MIXED = "mixed"

AccessToken = namedtuple(
    "AccessToken", ["value", "renew_at", "mode", "scope", "fingerprint"]
)


def now():
    """Return the clock used for the token lifetimes.

    A monotonic clock: the lifetimes come from the `expires_in` of the token responses,
    so neither the clock of the server nor its adjustments matter.
    """
    return time.monotonic()


def make_cache_key(dbname, provider_id, client_id, token_url, audience):
    """Return the cache key of a token. The client secret is never part of it."""
    digest = hashlib.sha256(
        "\0".join((client_id, token_url, audience)).encode()
    ).hexdigest()
    return (dbname, provider_id, digest)


def decode_jwt_claims(token):
    """Return the claims of a JWT, without verifying its signature, or {}.

    The token comes straight from the Payplug token endpoint over TLS; its claims are
    only read to check that its environment matches the provider, never to grant
    anything.
    """
    parts = token.split(".") if isinstance(token, str) else []
    if len(parts) != 3:
        return {}
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(payload.encode()))
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return {}
    return claims if isinstance(claims, dict) else {}


def get_token_scopes(token, scope=None):
    """Return the scopes of a token, from its `scp` claim and the response `scope`."""
    scopes = set()
    claim = decode_jwt_claims(token).get("scp")
    for value in (claim, scope):
        if isinstance(value, str):
            scopes.update(value.split())
        elif isinstance(value, (list, tuple)):
            scopes.update(item for item in value if isinstance(item, str))
    return scopes


def get_token_mode(scopes):
    """Return the environment of a token given its scopes.

    :param set scopes: The scopes of the token.
    :return: `test`, `live`, `mixed` (both) or `unknown` (neither).
    :rtype: str
    """
    is_test = MODE_TEST in scopes
    is_live = MODE_LIVE in scopes
    if is_test and is_live:
        return MODE_MIXED
    if is_test:
        return MODE_TEST
    if is_live:
        return MODE_LIVE
    return MODE_UNKNOWN


class TokenCache:
    """A thread-safe cache of access tokens, renewed before they expire."""

    def __init__(self, renewal_margin):
        self.renewal_margin = renewal_margin
        self._lock = threading.Lock()
        self._tokens = {}
        self._fetch_locks = {}
        # Random per process: the fingerprints of the secrets cannot be compared
        # outside of it.
        self._salt = secrets.token_bytes(32)

    def fingerprint(self, secret):
        """Return a fingerprint of the client secret, to detect its changes."""
        return hmac.new(self._salt, secret.encode(), hashlib.sha256).digest()

    def get(self, key, fingerprint):
        """Return the cached token if it is still valid for the given secret."""
        with self._lock:
            token = self._tokens.get(key)
        if token and token.fingerprint == fingerprint and now() < token.renew_at:
            return token
        return None

    def get_or_fetch(self, key, fingerprint, fetch):
        """Return the cached token, or fetch, cache and return a new one.

        Only one thread per key fetches a token; the others wait for it.

        :param tuple key: The cache key, from `make_cache_key`.
        :param bytes fingerprint: The fingerprint of the client secret.
        :param fetch: A callable returning `(value, expires_in, mode, scope)`. It may
            raise; nothing is cached then.
        :return: The token.
        :rtype: AccessToken
        """
        token = self.get(key, fingerprint)
        if token:
            return token
        with self._lock:
            fetch_lock = self._fetch_locks.setdefault(key, threading.Lock())
        with fetch_lock:
            token = self.get(key, fingerprint)  # Fetched by another thread meanwhile.
            if token:
                return token
            requested_at = now()
            value, expires_in, mode, scope = fetch()
            margin = min(self.renewal_margin, expires_in / 2)
            token = AccessToken(
                value, requested_at + expires_in - margin, mode, scope, fingerprint
            )
            with self._lock:
                self._tokens[key] = token
            return token

    def invalidate(self, dbname, provider_id):
        """Forget the tokens of a provider."""
        with self._lock:
            for key in [k for k in self._tokens if k[:2] == (dbname, provider_id)]:
                del self._tokens[key]

    def clear(self):
        with self._lock:
            self._tokens.clear()

    def keys(self):
        with self._lock:
            return list(self._tokens)


TOKEN_CACHE = TokenCache(renewal_margin=const.TOKEN_RENEWAL_MARGIN)
