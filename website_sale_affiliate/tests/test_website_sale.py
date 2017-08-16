# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import mock

from odoo import http
from odoo.tests.common import HttpCase

from .test_sale_common import SaleCase


class WebsiteSaleCase(HttpCase, SaleCase):
    def setUp(self):
        super(WebsiteSaleCase, self).setUp()
        self.opener.addheaders.extend([
            ('Accept-Language', 'test_language'),
            ('Referer', 'test_referrer'),
        ])
        self.Affiliate = self.env['sale.affiliate']
        self.get_request_mock = mock.MagicMock()
        self.get_request_mock.return_value = self.demo_request

    def get_session_from_url_open(self, **kwargs):
        try:
            url = '%(url)s?aff_ref=%(aff_ref)s&aff_key=%(aff_key)s' % kwargs
        except KeyError:
            url = '%(url)s?aff_ref=%(aff_ref)s' % kwargs
        self.url_open(url)
        return http.root.session_store.get(self.session_id)

    def test_shop(self):
        """Adds request id to session when aff_ref kwarg present"""
        self.demo_affiliate._patch_method('get_request', self.get_request_mock)
        try:
            kwargs = {'url': '/shop', 'aff_ref': str(self.demo_affiliate.id)}
            session = self.get_session_from_url_open(**kwargs)
            self.assertEqual(
                session.get('affiliate_request'),
                self.demo_request.id,
            )
        finally:
            self.demo_affiliate._revert_method('get_request')

    def test_product(self):
        """Adds request id to session when aff_ref kwarg present"""
        self.demo_affiliate._patch_method('get_request', self.get_request_mock)
        try:
            product = self.env['product.product'].search([
                ('website_published', '=', True),
            ], limit=1)
            kwargs = {
                'url': product.website_url,
                'aff_ref': self.demo_affiliate.id,
            }
            session = self.get_session_from_url_open(**kwargs)
            self.assertEqual(
                session.get('affiliate_request'),
                self.demo_request.id,
            )
        finally:
            self.demo_affiliate._revert_method('get_request')

    def test_store_affiliate_info_aff_key_absent(self):
        """Calls affiliate get_request method
        when aff_ref valid and aff_key kwarg absent"""
        self.demo_affiliate._patch_method('get_request', self.get_request_mock)
        try:
            kwargs = {'aff_ref': str(self.demo_affiliate.id)}
            self.url_open('/shop?aff_ref=%(aff_ref)s' % kwargs)
            self.get_request_mock.assert_called_once_with(**kwargs)
        finally:
            self.demo_affiliate._revert_method('get_request')

    def test_store_affiliate_info_aff_key_present(self):
        """Adds valid affiliate request in session that matches aff_key"""
        kwargs = {
            'url': '/shop',
            'aff_ref': self.demo_affiliate.id,
            'aff_key': self.demo_request.name,
        }
        session = self.get_session_from_url_open(**kwargs)
        affiliate_request = self.env['sale.affiliate.request'].search([
            ('id', '=', session.get('affiliate_request')),
        ])
        self.assertEqual(affiliate_request, self.demo_request)

    def test_store_affiliate_info_aff_ref_absent(self):
        """Does not add affiliate request to session when aff_ref absent"""
        self.url_open('/shop')
        session = http.root.session_store.get(self.session_id)
        self.assertFalse(session.get('affiliate_request'))

    def test_store_affiliate_info_aff_ref_no_matches(self):
        """Does not add affiliate request to session
        when there is no affiliate id matching aff_ref"""
        kwargs = {'url': '/shop', 'aff_ref': 0}
        session = self.get_session_from_url_open(**kwargs)
        self.assertFalse(session.get('affiliate_request'))

    def test_store_affiliate_info_aff_ref_invalid(self):
        """Does not add affiliate request to session when aff_ref invalid"""
        kwargs = {'url': '/shop', 'aff_ref': 'not_int'}
        session = self.get_session_from_url_open(**kwargs)
        self.assertFalse(session.get('affiliate_request'))

    def test_store_affiliate_info_new_aff_ref_replace_existing(self):
        """Replaces existing affiliate_request in session
        when new aff_ref kwarg provided"""
        kwargs = {'url': '/shop', 'aff_ref': self.demo_affiliate.id}
        session = self.get_session_from_url_open(**kwargs)
        old_request = session.get('affiliate_request')

        kwargs['aff_ref'] = self.demo_affiliate_2.id
        session = self.get_session_from_url_open(**kwargs)
        new_request = session.get('affiliate_request')

        self.assertNotEqual(new_request, old_request)

    def test_store_affiliate_info_new_aff_key_replace_existing(self):
        """Replaces existing affiliate_request in session
        when new aff_key kwarg provided"""
        kwargs = {
            'url': '/shop',
            'aff_ref': self.demo_affiliate.id,
            'aff_key': 'testing',
        }
        session = self.get_session_from_url_open(**kwargs)
        old_request = session.get('affiliate_request')

        kwargs['aff_key'] = self.demo_request.name
        session = self.get_session_from_url_open(**kwargs)
        new_request = session.get('affiliate_request')

        self.assertNotEqual(new_request, old_request)

    def test_store_affiliate_info_preserves_existing(self):
        """Preserves existing affiliate_request in session
        when no new aff_key or aff_ref provided"""
        kwargs = {
            'url': '/shop',
            'aff_ref': self.demo_affiliate.id,
            'aff_key': self.demo_request.name,
        }
        session = self.get_session_from_url_open(**kwargs)
        old_request = session.get('affiliate_request')

        self.url_open('/shop')
        session = http.root.session_store.get(self.session_id)
        new_request = session.get('affiliate_request')

        self.assertEqual(new_request, old_request)
