# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import http
from odoo.tests.common import HttpCase


class WebsiteSaleCase(HttpCase):
    def setUp(self):
        super(WebsiteSaleCase, self).setUp()
        self.test_id = '1'
        self.test_id_invalid = 'not_int'
        self.test_id_old = '2'
        self.test_key = 'test_key'
        self.test_key_old = 'old_key'

    def setup_old_session_vals(self):
        self.session['affiliate_id'] = self.test_id_old
        self.session['affiliate_key'] = self.test_key_old
        http.root.session_store.save(self.session)

    def test_shop(self):
        """Adds valid aff_ref kwarg of shop urls to session"""
        kwargs = {'id': self.test_id}
        shop_url = '/shop?aff_ref=%(id)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertEqual(session.get('affiliate_id'), int(self.test_id))

    def test_product(self):
        """Adds valid aff_ref kwarg of product urls to session"""
        product = self.env['product.product'].search([
            ('website_published', '=', True),
        ], limit=1)
        kwargs = {'url': product.website_url, 'id': self.test_id}
        product_url = '%(url)s?aff_ref=%(id)s' % kwargs
        self.url_open(product_url)
        session = http.root.session_store.get(self.session_id)
        self.assertEqual(session.get('affiliate_id'), int(self.test_id))

    def test_store_affiliate_info_aff_ref_and_aff_key_present(self):
        """Adds aff_ref and aff_key kwargs to session
        when aff_ref present and valid"""
        kwargs = {'id': self.test_id, 'key': self.test_key}
        shop_url = '/shop?aff_ref=%(id)s&aff_key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertEqual(
            session.get('affiliate_id'), int(self.test_id),
            'aff_ref kwarg not added properly',
        )
        self.assertEqual(
            session.get('affiliate_key'), self.test_key,
            'aff_key kwarg not added properly',
        )

    def test_store_affiliate_info_aff_ref_absent(self):
        """Does not add aff_ref kwarg to session when aff_ref absent"""
        kwargs = {'key': self.test_key}
        shop_url = '/shop?aff_key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertIsNone(session.get('affiliate_id'))

    def test_store_affiliate_info_aff_ref_invalid(self):
        """Does not add aff_ref kwarg to session when aff_ref invalid"""
        kwargs = {'id': self.test_id_invalid, 'key': self.test_key}
        shop_url = '/shop?aff_ref=%(id)s&aff_key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertIsNone(session.get('affiliate_id'))

    def test_store_affiliate_info_replace_existing(self):
        """Replaces existing affiliate_id and affiliate_key in session"""
        self.setup_old_session_vals()

        kwargs = {'id': self.test_id, 'key': self.test_key}
        shop_url = '/shop?aff_ref=%(id)s&aff_key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)

        self.assertEqual(
            session.get('affiliate_id'), int(self.test_id),
            'affiliate_id not replaced',
        )
        self.assertEqual(
            session.get('affiliate_key'), self.test_key,
            'affiliate_key not replaced',
        )

    def test_store_affiliate_info_does_not_remove_existing_without_new(self):
        """Does not remove existing affiliate_id and affiliate_key in session
        if no new aff_ref or aff_key kwargs info present"""
        self.setup_old_session_vals()

        self.url_open('/shop')
        session = http.root.session_store.get(self.session_id)

        self.assertEqual(
            session.get('affiliate_id'), self.test_id_old,
            'affiliate_id removed',
        )
        self.assertEqual(
            session.get('affiliate_key'), self.test_key_old,
            'affiliate_key removed',
        )

    def test_store_affiliate_info_remove_existing_key(self):
        """Remove existing affiliate_key in session
        when new aff_ref present but new aff_key absent"""
        self.setup_old_session_vals()

        kwargs = {'id': self.test_id}
        shop_url = '/shop?aff_ref=%(id)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)

        self.assertEqual(
            session.get('affiliate_id'), int(self.test_id),
            'affiliate_id not replaced',
        )
        self.assertEqual(
            session.get('affiliate_key'), None,
            'affiliate_key not removed',
        )
