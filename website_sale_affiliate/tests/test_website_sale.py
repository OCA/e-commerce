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
        self.test_key = 'test_key'

    def test_shop_ref_present(self):
        """Adds ref kwarg to session when ref present and valid"""
        kwargs = {'id': self.test_id}
        shop_url = '/shop?ref=%(id)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertEqual(session.get('affiliate_id'), int(self.test_id))

    def test_shop_ref_and_key_present(self):
        """Adds ref and key kwargs to session when ref present and valid"""
        kwargs = {'id': self.test_id, 'key': self.test_key}
        shop_url = '/shop?ref=%(id)s&key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertEqual(
            session.get('affiliate_id'), int(self.test_id),
            'Ref kwarg not added properly',
        )
        self.assertEqual(
            session.get('affiliate_key'), self.test_key,
            'Key kwarg not added properly',
        )

    def test_shop_ref_absent(self):
        """Does not add either ref or key kwargs to session when ref absent"""
        kwargs = {'key': self.test_key}
        shop_url = '/shop?key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertIsNone(
            session.get('affiliate_id'),
            'Ref kwarg added improperly',
        )
        self.assertIsNone(
            session.get('affiliate_key'),
            'Key kwarg added improperly',
        )

    def test_shop_ref_invalid(self):
        """Does not add either ref or key kwargs to session when ref invalid"""
        kwargs = {'id': self.test_id_invalid, 'key': self.test_key}
        shop_url = '/shop?ref=%(id)s&key=%(key)s' % kwargs
        self.url_open(shop_url)
        session = http.root.session_store.get(self.session_id)
        self.assertIsNone(
            session.get('affiliate_id'),
            'Ref kwarg added improperly',
        )
        self.assertIsNone(
            session.get('affiliate_key'),
            'Key kwarg added improperly',
        )
