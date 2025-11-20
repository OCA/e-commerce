# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import logging
from os.path import dirname, join

import requests
import werkzeug
from requests import PreparedRequest, Session
from vcr import VCR

from odoo.tests import Form, HttpCase, TransactionCase
from odoo.tools import mute_logger

_super_send = requests.Session.send

logging.getLogger("vcr").setLevel(logging.WARNING)

recorder = VCR(
    record_mode="once",
    cassette_library_dir=join(dirname(__file__), "vcr_cassettes"),
    path_transformer=VCR.ensure_suffix(".yaml"),
    filter_headers=["Authorization"],
    decode_compressed_response=True,
)


class TestDeliverySendCloud(TransactionCase):
    @classmethod
    def _request_handler(cls, s: Session, r: PreparedRequest, /, **kw):
        """
        Override to allow requests to the sendcloud API
        because odoo17 only permit calls to localhost
        (see https://github.com/odoo/odoo/blob/17.0/odoo/tests/common.py#L265 )
        """
        url = werkzeug.urls.url_parse(r.url)
        if url.host in ("f482-185-247-144-87.eu.ngrok.io", "panel.sendcloud.sc"):
            return _super_send(s, r, **kw)
        return super()._request_handler(s=s, r=r, **kw)

    @mute_logger("py.warnings")
    def setUp(self):
        super().setUp()
        if not self.registry.in_test_mode():
            self.registry.enter_test_mode(self.cr)
        form = Form(self.env["sendcloud.integration.wizard"])
        wizard = form.save()
        wizard.base_url = "https://f482-185-247-144-87.eu.ngrok.io"
        with recorder.use_cassette("get_integration"):
            wizard.button_update()
        self.integration = self.env["sendcloud.integration"].search([])
        self.assertEqual(len(self.integration), 1)
        self.integration.public_key = "test"
        self.integration.secret_key = "test"
        self.integration.sendcloud_code = 241526

    @classmethod
    def tearDownClass(cls):
        cls.registry.leave_test_mode()
        super().tearDownClass()

    @mute_logger("py.warnings")
    def test_sync_wizard(self):
        sendcloud_sync_wizard_rec = self.env["sendcloud.sync.wizard"].create(
            {
                "publish_all_shipping_methods": True,
                "brands": False,
                "returns": False,
                "parcel_statuses": False,
                "parcels": False,
                "invoices": False,
                "sender_addresses": False,
                "shipping_methods": True,
            }
        )
        delivery_carrier_obj = self.env["delivery.carrier"]
        self.assertFalse(
            delivery_carrier_obj.search(
                [("delivery_type", "=", "sendcloud"), ("website_published", "=", True)],
                limit=1,
            )
        )
        with recorder.use_cassette("shipping_methods"):
            sendcloud_sync_wizard_rec.button_sync()
        self.assertTrue(
            delivery_carrier_obj.search(
                [("delivery_type", "=", "sendcloud"), ("website_published", "=", True)]
            )
        )

    @mute_logger("py.warnings")
    def test_website_brand_wizard(self):
        sendcloud_website_brand_wizard_rec = self.env[
            "sendcloud.website.brand.wizard"
        ].create({})
        sendcloud_website_brand_wizard_rec.button_update()


class TestWebsiteSendCloud(HttpCase):
    @classmethod
    def _request_handler(cls, s: Session, r: PreparedRequest, /, **kw):
        """
        Override to allow requests to the sendcloud API
        because odoo17 only permit calls to localhost
        (see https://github.com/odoo/odoo/blob/17.0/odoo/tests/common.py#L265 )
        """
        url = werkzeug.urls.url_parse(r.url)
        if url.host in ("f482-185-247-144-87.eu.ngrok.io", "panel.sendcloud.sc"):
            return _super_send(s, r, **kw)
        return super()._request_handler(s, r, **kw)

    @mute_logger("py.warnings")
    def setUp(self):
        super().setUp()
        form = Form(self.env["sendcloud.integration.wizard"])
        wizard = form.save()
        wizard.base_url = "https://f482-185-247-144-87.eu.ngrok.io"
        with recorder.use_cassette("get_integration"):
            wizard.button_update()
        self.integration = self.env["sendcloud.integration"].search([])
        self.assertEqual(len(self.integration), 1)
        self.integration.public_key = "test"
        self.integration.secret_key = "test"
        self.integration.sendcloud_code = 241526
        with recorder.use_cassette("integrations"):
            self.integration.action_sendcloud_update_integrations()
        with recorder.use_cassette("shipping_methods"):
            self.env["sendcloud.sync.wizard"].create(
                {
                    "publish_all_shipping_methods": True,
                    "brands": False,
                    "returns": False,
                    "parcel_statuses": False,
                    "parcels": False,
                    "invoices": False,
                    "sender_addresses": False,
                    "shipping_methods": True,
                }
            ).button_sync()
        with recorder.use_cassette("sender_address"):
            self.env["sendcloud.sender.address"].sendcloud_sync_sender_address()

    def test_sendcloud_update_service_point_address(self):
        self.env["res.users"].create(
            {
                "name": "Temporary User",
                "login": "temp_user",
                "password": "temp_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.ref("base.group_portal"),
                        ],
                    )
                ],
                "country_id": self.env.ref("base.nl").id,
                "street": "Bloemstraat 42",
                "zip": "4817RH",
                "city": "Groningen",
                "phone": "+31 6 12345678",
                "state_id": self.env.ref("base.state_nl_gr").id,
                "email": "admin@yourcompany.example.com",
                "vat": "NL219987701B73",
            }
        )
        self.start_tour("/", "website_sendcloud_oca", login="temp_user")
