# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import mock

from odoo import http
from odoo.tests.common import HttpCase

from ..controllers.main import WebsiteSale
from .common import SaleCase

CONTROLLER_PATH = "odoo.addons.website_sale_affiliate.controllers.main"


class WebsiteSaleCase(HttpCase, SaleCase):
    def setUp(self):
        super(WebsiteSaleCase, self).setUp()
        self.controller = WebsiteSale()
        # self.opener.addheaders.extend(
        #     [
        #         ("Accept-Language", "test_language"),
        #         ("Referer", "test_referrer"),
        #     ]
        # )
        self.Affiliate = self.env["sale.affiliate"]
        self.find_from_kwargs_mock = mock.MagicMock()
        self.get_request_mock = mock.MagicMock()

    def test_shop(self):
        """Adds request id to session when aff_ref kwarg present"""
        self.get_request_mock.return_value = self.demo_request
        self.demo_affiliate._patch_method("get_request", self.get_request_mock)
        try:
            data = {
                "url": "/shop",
                "aff_ref": str(self.demo_affiliate.id),
            }
            req = self.url_open("%(url)s?aff_ref=%(aff_ref)s" % data)
            session = [
                i.strip()
                for i in req.headers["Set-Cookie"].split(",")
                if "session_id" in i
            ]
            if session:
                session = session[0]
                session_id = session[session.index("=") + 1 : session.index(";")]
                session = http.root.session_store.get(session_id)
                self.assertEqual(
                    session.get("affiliate_request"),
                    self.demo_request.id,
                )
        finally:
            self.demo_affiliate._revert_method("get_request")

    def test_product(self):
        """Adds request id to session when aff_ref kwarg present"""
        self.get_request_mock.return_value = self.demo_request
        self.demo_affiliate._patch_method("get_request", self.get_request_mock)
        try:
            data = {
                "url": self.demo_product.website_url,
                "aff_ref": str(self.demo_affiliate.id),
            }
            req = self.url_open("%(url)s?aff_ref=%(aff_ref)s" % data)
            session = [
                i.strip()
                for i in req.headers["Set-Cookie"].split(",")
                if "session_id" in i
            ]
            if session:
                session = session[0]
                session_id = session[session.index("=") + 1 : session.index(";")]
                session = http.root.session_store.get(session_id)
                self.assertEqual(
                    session.get("affiliate_request", 1),
                    self.demo_request.id,
                )
        finally:
            self.demo_affiliate._revert_method("get_request")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_calls_find_from_kwargs(self, request_mock):
        """Calls affiliate find_from_kwargs method"""
        request_mock.env = self.env
        self.find_from_kwargs_mock.return_value = None
        self.Affiliate._patch_method(
            "find_from_kwargs",
            self.find_from_kwargs_mock,
        )
        try:
            kwargs = {}
            self.controller._store_affiliate_info(**kwargs)
            self.find_from_kwargs_mock.assert_called_once_with(**kwargs)
        finally:
            self.Affiliate._revert_method("find_from_kwargs")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_calls_get_request(self, request_mock):
        """Calls affiliate get_request method with provided kwargs
        when affiliate matching aff_ref is found"""
        request_mock.env = self.env
        self.Affiliate._patch_method("get_request", self.get_request_mock)
        try:
            kwargs = {
                "aff_ref": self.demo_affiliate.id,
                "aff_key": self.demo_request.id,
            }
            self.controller._store_affiliate_info(**kwargs)
            self.get_request_mock.assert_called_once_with(**kwargs)
        finally:
            self.Affiliate._revert_method("get_request")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_does_not_call_get_request(
        self,
        request_mock,
    ):
        """Does not call affiliate get_request method
        when affiliate matching aff_ref is not found"""
        request_mock.env = self.env
        self.Affiliate._patch_method("get_request", self.get_request_mock)
        try:
            kwargs = {}
            self.controller._store_affiliate_info(**kwargs)
            self.assertFalse(self.get_request_mock.called)
        finally:
            self.Affiliate._revert_method("get_request")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_adds_affiliate_request_to_session(
        self,
        request_mock,
    ):
        """Adds affiliate request to session when found"""
        request_mock.env = self.env
        request_mock.session = {}
        self.get_request_mock.return_value = self.demo_request
        self.Affiliate._patch_method("get_request", self.get_request_mock)
        try:
            kwargs = {"aff_ref": self.demo_affiliate.id}
            self.controller._store_affiliate_info(**kwargs)
            self.assertEqual(
                request_mock.session["affiliate_request"],
                self.demo_request.id,
            )
        finally:
            self.Affiliate._revert_method("get_request")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_does_not_add_affiliate_request_to_session(
        self,
        request_mock,
    ):
        """Does not add affiliate request to session
        when matching affiliate not found"""
        request_mock.env = self.env
        request_mock.session = {}
        self.find_from_kwargs_mock.return_value = None
        self.Affiliate._patch_method(
            "find_from_kwargs",
            self.find_from_kwargs_mock,
        )
        try:
            kwargs = {}
            self.controller._store_affiliate_info(**kwargs)
            self.assertIsNone(request_mock.session.get("affiliate_request"))
        finally:
            self.Affiliate._revert_method("find_from_kwargs")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_replaces_existing_session_data(
        self,
        request_mock,
    ):
        """Replaces existing affiliate request in session
        when new request found"""
        request_mock.env = self.env
        request_mock.session = {"affiliate_request": 0}
        self.get_request_mock.return_value = self.demo_request
        self.Affiliate._patch_method("get_request", self.get_request_mock)
        try:
            kwargs = {"aff_ref": self.demo_affiliate.id}
            self.controller._store_affiliate_info(**kwargs)
            self.assertEqual(
                request_mock.session["affiliate_request"],
                self.demo_request.id,
            )
        finally:
            self.Affiliate._revert_method("get_request")

    @mock.patch("%s.request" % CONTROLLER_PATH)
    def test_store_affiliate_info_preserves_existing_session_data(
        self,
        request_mock,
    ):
        """Preserves old affiliate request in session
        when no new affiliate found"""
        request_mock.env = self.env
        request_mock.session = {"affiliate_request": 0}
        self.find_from_kwargs_mock.return_value = None
        self.Affiliate._patch_method("find_from_kwargs", self.find_from_kwargs_mock)
        try:
            kwargs = {}
            self.controller._store_affiliate_info(**kwargs)
            self.assertEqual(request_mock.session["affiliate_request"], 0)
        finally:
            self.Affiliate._revert_method("find_from_kwargs")
