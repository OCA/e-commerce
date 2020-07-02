# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import patch

from odoo import fields
from odoo.tests.common import SavepointCase

MODULE_PATH = 'odoo.addons.website_sale_affiliate'
AFFILIATE_REQUEST_PATH = MODULE_PATH + '.models.sale_affiliate_request.request'


class TestWebsiteSaleAffiliateProductRestriction(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestWebsiteSaleAffiliateProductRestriction, cls).setUpClass()
        seq = cls.env.ref('website_sale_affiliate.request_sequence')
        cls.affiliate = cls.env['sale.affiliate'].create({
            'name': 'my affiliate',
            'company_id': cls.env.ref('base.main_company').id,
            'sequence_id': seq.id,
            'valid_hours': 24,
            'valid_sales': 100,
        })
        request_patcher = patch(AFFILIATE_REQUEST_PATH)
        request_mock = request_patcher.start()
        request_mock.configure_mock(session={})
        cls.fake_session = request_mock.session
        cls.addCleanup(request_patcher.stop)
        cls.req = cls.env['sale.affiliate.request'].create({
            'name': 'test affiliate request',
            'affiliate_id': cls.affiliate.id,
            'date': fields.Datetime.now(),
            'ip': '127.0.0.1',
            'referrer': 'https://commown.fr',
            'user_agent': 'firefox',
            'accept_language': 'fr',
        })
        cls.p1 = cls.env.ref('product.product_product_1').product_tmpl_id
        cls.p2 = cls.env.ref('product.product_product_2').product_tmpl_id
        cls.p3 = cls.env.ref('product.product_product_3').product_tmpl_id

    def create_sale(self, products=None, state='sent', create_date=None):
        partner_1 = self.env.ref('base.res_partner_1')
        if products is None:
            products = [self.env.ref('product.product_product_1')]
        data = {
            'partner_id': partner_1.id,
            'partner_invoice_id': partner_1.id,
            'partner_shipping_id': partner_1.id,
            'pricelist_id': self.env.ref('product.list0').id,
            'state': state,
            'order_line': [],
            }
        for product in products:
            data['order_line'].append((0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
            }))
        sale = self.env['sale.order'].create(data)
        if create_date is not None:
            self.cr.execute('UPDATE sale_order SET create_date=%s WHERE id=%s',
                            (create_date, sale.id))

        return sale

    def test_sale_order_without_product_restriction(self):
        self.fake_session['affiliate_request'] = self.req.id
        self.create_sale([self.p1, self.p2], 'sent')

        self.fake_session['affiliate_request'] = self.req.id
        self.create_sale([self.p2, self.p3], 'draft')
        self.create_sale([self.p3], 'sent')
        self.create_sale([self.p1], 'sent')
        self.create_sale([self.p2], 'sent')

        self.fake_session['affiliate_request'] = self.req.id
        self.fake_session['affiliate_request'] = self.req.id

        self.assertAlmostEqual(self.affiliate.sales_per_request, 4)
        self.assertAlmostEqual(self.affiliate.conversion_rate, 1)

    def test_sale_order_with_product_restriction(self):
        self.affiliate.restriction_product_tmpl_ids |= (self.p2 | self.p3)

        self.fake_session['affiliate_request'] = self.req.id
        self.create_sale([self.p1], 'sent')

        self.fake_session['affiliate_request'] = self.req.id
        self.create_sale([self.p1, self.p3], 'sent')
        self.create_sale([self.p2], 'sent')

        self.fake_session['affiliate_request'] = self.req.id
        self.fake_session['affiliate_request'] = self.req.id

        self.assertEqual(self.affiliate.sales_per_request, 2)
        self.assertAlmostEqual(self.affiliate.conversion_rate, 1)
