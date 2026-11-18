# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.addons.payment.tests.common import PaymentCommon

from .. import const, oauth
from .fake_payplug import OAUTH2_CLIENTS, FakePayplugServer

TEST_SECRET_KEY = "sk_test_odoo_payplug_fake_key"  # Only valid on the fake server.
# Fake OAuth2 clients, only valid on the fake server.
TEST_CLIENT_ID = "fake_client_test"
TEST_CLIENT_SECRET = OAUTH2_CLIENTS[TEST_CLIENT_ID][0]
LIVE_CLIENT_ID = "fake_client_live"
LIVE_CLIENT_SECRET = OAUTH2_CLIENTS[LIVE_CLIENT_ID][0]


class PayplugCommon(PaymentCommon):
    """A Payplug provider in test mode talking to a local fake Payplug API."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.fake_payplug = FakePayplugServer().start()
        cls.addClassCleanup(cls.fake_payplug.stop)
        cls.env["ir.config_parameter"].sudo().set_param(
            const.API_BASE_URL_PARAM, cls.fake_payplug.api_url
        )

        cls.payplug = cls._prepare_provider(
            "payplug", update_values={"payplug_secret_key": TEST_SECRET_KEY}
        )
        cls.provider = cls.payplug
        cls.currency = cls.currency_euro
        cls.amount = 49.90
        cls.payment_method = cls.env.ref("payment.payment_method_card")
        cls.payment_method_id = cls.payment_method.id
        cls.payment_method_code = cls.payment_method.code

    def setUp(self):
        super().setUp()
        self.fake_payplug.state.reset()
        oauth.TOKEN_CACHE.clear()
        self.addCleanup(oauth.TOKEN_CACHE.clear)

    # === Helpers === #

    def _create_payplug_payment(self, **tx_values):
        """Create a transaction and its payment on the fake Payplug, like the checkout.

        :return: The transaction and the processing values.
        """
        tx = self._create_transaction("redirect", **tx_values)
        processing_values = tx._get_processing_values()
        return tx, processing_values

    def _notification(self, obj):
        return {key: obj[key] for key in ("id", "object", "is_live") if key in obj} | (
            {"payment_id": obj["payment_id"]} if "payment_id" in obj else {}
        )


class PayplugOAuth2Common(PayplugCommon):
    """The same Payplug provider, authenticated with an OAuth2 client of the Test
    environment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payplug.write(
            {
                "payplug_auth_method": "oauth2",
                "payplug_client_id": TEST_CLIENT_ID,
                "payplug_client_secret": TEST_CLIENT_SECRET,
                "payplug_secret_key": False,
            }
        )
