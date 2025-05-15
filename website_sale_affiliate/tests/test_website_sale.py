# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from urllib.parse import urlencode

from odoo import http
from odoo.tests import HttpCase, tagged

from .common import SaleCase

CONTROLLER_PATH = "odoo.addons.website_sale_affiliate.controllers.main"


@tagged("post_install", "-at_install")
class WebsiteSaleCase(HttpCase, SaleCase):
    def setUp(self):
        super().setUp()
        self.authenticate(None, None)
        self.opener.headers["Accept-Language"] = "test_language"
        self.opener.headers["Referer"] = "test_referrer"

    def _req(self, path, **params):
        url = self.base_url() + path.split("#")[0] + "?" + urlencode(params)
        self.opener.get(url, timeout=12000, allow_redirects=True)

    def test_shop(self):
        """Adds request id to session when aff_ref kwarg present"""
        self._req(
            "/shop",
            aff_ref=self.demo_affiliate.id,
            aff_key=self.demo_request.name,
        )
        session = http.root.session_store.get(self.session.sid)
        self.assertEqual(
            session.get("affiliate_request"),
            self.demo_request.id,
        )

    def test_product(self):
        """Adds request id to session when aff_ref kwarg present"""
        self._req(
            self.demo_product.website_url,
            aff_ref=self.demo_affiliate.id,
            aff_key=self.demo_request.name,
        )
        session = http.root.session_store.get(self.session.sid)
        self.assertEqual(
            session.get("affiliate_request"),
            self.demo_request.id,
        )

    def test_no_affiliate_request_when_aff_ref_not_found(self):
        """Does not add affiliate request to session
        when affiliate matching aff_ref is not found"""
        self._req(
            "/shop",
            aff_ref=0,
            aff_key=self.demo_request.name,
        )
        session = http.root.session_store.get(self.session.sid)
        self.assertFalse(session.get("affiliate_request"))

    def test_add_affiliate_request_when_key_is_false(self):
        """Add an affiliate request even if the key is false"""
        self._req(
            "/shop",
            aff_ref=self.demo_affiliate.id,
            aff_key="this_is_a_false_key",
        )
        session = http.root.session_store.get(self.session.sid)
        self.assertTrue(session.get("affiliate_request"))
