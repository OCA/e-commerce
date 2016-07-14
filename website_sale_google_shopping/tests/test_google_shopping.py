# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

import openerp


class TestGoogleShopping(openerp.tests.HttpCase):

    def setUp(self):
        super(TestGoogleShopping, self).setUp()

    def test_cache_feed(self):
        url = '/google-shopping.xml'
        page = self.url_open(url)
        code = page.getcode()
        self.assertIn(
            code,
            xrange(200, 300),
            'Fetching %s returned error response (%d)' % (url, code))

        page = self.url_open(url)
        code = page.getcode()
        self.assertIn(
            code,
            xrange(200, 300),
            'Fetching %s returned error response (%d)' % (url, code))

        website_id = self.ref('website.default_website')
        website_obj = self.env['website']
        website = website_obj.browse(website_id)
        google_feed_expiry_time = website.google_feed_expiry_time
        website.write({'google_feed_expiry_time': 0})
        self.env.cr.commit()

        page = self.url_open(url)
        code = page.getcode()
        self.assertIn(
            code,
            xrange(200, 300),
            'Fetching %s returned error response (%d)' % (url, code))

        website.write({'google_feed_expiry_time': google_feed_expiry_time})
        self.env.cr.commit()
