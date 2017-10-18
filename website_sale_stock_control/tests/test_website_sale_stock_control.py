# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import urllib
from lxml import html

from openerp.tests.common import HttpCase


class WebsiteSaleStockControlCase(HttpCase):
    def setUp(self):
        super(WebsiteSaleStockControlCase, self).setUp()
        with self.cursor() as cr:
            env = self.env(cr)
            self.public_user = env.ref('base.public_partner')
            self.attribute1 = env['product.attribute'].create({
                'name': 'Test Attribute 1',
                'value_ids': [
                    (0, 0, {'name': 'Value 1'}),
                    (0, 0, {'name': 'Value 2'}),
                ],
            })
            self.attribute2 = env['product.attribute'].create({
                'name': 'Test Attribute 2',
                'value_ids': [
                    (0, 0, {'name': 'Value X'}),
                    (0, 0, {'name': 'Value Y'}),
                ],
            })
            self.product_tmpl = env['product.template'].create({
                'name': 'Test template',
                'type': 'product',
                'website_published': True,
                'inventory_availability': 'always',
                'attribute_line_ids': [
                    (0, 0, {
                        'attribute_id': self.attribute1.id,
                        'value_ids': [(6, 0, self.attribute1.value_ids.ids)],
                    }),
                    (0, 0, {
                        'attribute_id': self.attribute2.id,
                        'value_ids': [(6, 0, self.attribute2.value_ids.ids)],
                    }),
                ],
            })

    def data_post(self, url=None, data=None, timeout=10):
        data_encode = None
        if data:
            data_encode = urllib.urlencode(data)
        doc = self.url_open(url, data=data_encode, timeout=timeout)
        return doc

    def test_shop_render(self):
        res = self.data_post(url='/shop').read()
        res_html = html.document_fromstring(res)
        query = u"""
            .//div[@id='no_stock']
        """
        no_stock = res_html.xpath(query)
        self.assertTrue(no_stock)

    def update_on_hand(self, env, variant=False, new_qty=0.0):
        """
        :param product: Product or template object
        :param new_qty: New quantities
        :return:
        """
        product_tmpl = self.product_tmpl.with_env(env)
        product = variant or product_tmpl.product_variant_ids[0]
        location = env['stock.location'].search([
            ('usage', '=', 'internal')
        ])[:1]
        stock_change_obj = env['stock.change.product.qty']
        vals = {
            'product_id': product.id,
            'product_tmpl_id': product_tmpl.id,
            'new_quantity': new_qty,
            'location_id': location.id,
        }
        wiz = stock_change_obj.create(vals)
        wiz.change_product_qty()

    def test_shop_variant_stock(self):
        with self.cursor() as cr:
            env = self.env(cr)
            self.update_on_hand(env, new_qty=5.0)
        res = self.data_post(url='/shop').read()
        res_html = html.document_fromstring(res)
        query = u"""
            .//div[@id='no_stock']
        """
        no_stock = res_html.xpath(query)
        self.assertFalse(no_stock)
