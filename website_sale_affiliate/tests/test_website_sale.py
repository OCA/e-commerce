# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from unittest import mock

from werkzeug.datastructures import MultiDict

from odoo.tests.common import HttpCase

from odoo.addons.website.tools import MockRequest

from ..controllers.main import WebsiteSale
from .common import SaleCase

CONTROLLER_PATH = "odoo.addons.website_sale_affiliate.controllers.main"


class WebsiteSaleCase(HttpCase, SaleCase):
    def setUp(self):
        super().setUp()
        self.controller = WebsiteSale()
        self.opener.headers.update(
            {
                "Accept-Language": "test_language",
                "Referer": "test_referrer",
            }
        )
        self.Affiliate = self.env["sale.affiliate"]
        self.find_from_kwargs_mock = mock.MagicMock()
        self.get_request_mock = mock.MagicMock()

    def test_shop(self):
        """Adds request id to session when aff_ref kwarg present"""
        data = {
            "url": "/shop",
            "aff_ref": str(self.demo_affiliate.id),
        }
        self.authenticate(None, None)
        self.url_open(
            f"{data['url']}?aff_ref={data['aff_ref']}",
            headers={"User-Agent": "test", "Accept-Language": "en-US"},
        )
        cookies = self.opener.cookies
        session_id = None
        for cookie in cookies:
            if cookie.name == "session_id":
                session_id = cookie.value
                break
        from odoo.http import root

        session = root.session_store.get(session_id)

        aff_req_id = session.get("affiliate_request")
        self.assertTrue(aff_req_id)

    def test_store_affiliate_info_calls_find_from_kwargs(self):
        """Calls affiliate find_from_kwargs method"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            self.find_from_kwargs_mock.return_value = None
            patcher = mock.patch.object(
                type(self.Affiliate), "find_from_kwargs", self.find_from_kwargs_mock
            )
            patcher.start()
            try:
                kwargs = {}
                self.controller._store_affiliate_info(**kwargs)
                self.find_from_kwargs_mock.assert_called_once_with(**kwargs)
            finally:
                patcher.stop()

    def test_store_affiliate_info_calls_get_request(self):
        """Calls affiliate get_request method with provided kwargs
        when affiliate matching aff_ref is found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            patcher = mock.patch.object(
                type(self.Affiliate), "get_request", self.get_request_mock
            )
            patcher.start()
            try:
                kwargs = {
                    "aff_ref": self.demo_affiliate.id,
                    "aff_key": self.demo_request.id,
                }
                self.controller._store_affiliate_info(**kwargs)
                self.get_request_mock.assert_called_once_with(**kwargs)
            finally:
                patcher.stop()

    def test_store_affiliate_info_does_not_call_get_request(
        self,
    ):
        """Does not call affiliate get_request method
        when affiliate matching aff_ref is not found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            patcher = mock.patch.object(
                type(self.Affiliate), "get_request", self.get_request_mock
            )
            patcher.start()
            try:
                kwargs = {}
                self.controller._store_affiliate_info(**kwargs)
                self.assertFalse(self.get_request_mock.called)
            finally:
                patcher.stop()

    def test_store_affiliate_info_adds_affiliate_request_to_session(
        self,
    ):
        """Adds affiliate request to session when found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            request_mock.session = {}
            request_mock.httprequest.args = MultiDict()
            request_mock.httprequest.form = MultiDict()
            self.get_request_mock.return_value = self.demo_request
            patcher = mock.patch.object(
                type(self.Affiliate), "get_request", self.get_request_mock
            )
            patcher.start()
            try:
                kwargs = {"aff_ref": self.demo_affiliate.id}
                self.controller._store_affiliate_info(**kwargs)
                self.assertEqual(
                    request_mock.session["affiliate_request"],
                    self.demo_request.id,
                )
            finally:
                patcher.stop()

    def test_store_affiliate_info_does_not_add_affiliate_request_to_session(
        self,
    ):
        """Does not add affiliate request to session
        when matching affiliate not found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            request_mock.session = {}
            request_mock.httprequest.args = MultiDict()
            request_mock.httprequest.form = MultiDict()
            self.find_from_kwargs_mock.return_value = None
            patcher = mock.patch.object(
                type(self.Affiliate), "find_from_kwargs", self.find_from_kwargs_mock
            )
            patcher.start()
            try:
                kwargs = {}
                self.controller._store_affiliate_info(**kwargs)
                self.assertIsNone(request_mock.session.get("affiliate_request"))
            finally:
                patcher.stop()

    def test_store_affiliate_info_replaces_existing_session_data(
        self,
    ):
        """Replaces existing affiliate request in session
        when new request found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            request_mock.session = {"affiliate_request": 0}
            self.get_request_mock.return_value = self.demo_request
            patcher = mock.patch.object(
                type(self.Affiliate), "get_request", self.get_request_mock
            )
            patcher.start()
            try:
                kwargs = {"aff_ref": self.demo_affiliate.id}
                self.controller._store_affiliate_info(**kwargs)
                self.assertEqual(
                    request_mock.session["affiliate_request"],
                    self.demo_request.id,
                )
            finally:
                patcher.stop()

    def test_store_affiliate_info_preserves_existing_session_data(
        self,
    ):
        """Preserves old affiliate request in session
        when no new affiliate found"""
        with MockRequest(self.env) as request_mock:
            request_mock.env = self.env
            request_mock.session = {"affiliate_request": 0}
            self.find_from_kwargs_mock.return_value = None
            patcher = mock.patch.object(
                type(self.Affiliate), "find_from_kwargs", self.find_from_kwargs_mock
            )
            patcher.start()
            try:
                kwargs = {}
                self.controller._store_affiliate_info(**kwargs)
                self.assertEqual(request_mock.session["affiliate_request"], 0)
            finally:
                patcher.stop()
