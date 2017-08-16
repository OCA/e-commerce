# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.tests.common import TransactionCase


class SaleCase(TransactionCase):
    def setUp(self):
        super(SaleCase, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.products = {
            'prod_order': self.env.ref('product.product_order_01'),
            'prod_del': self.env.ref('product.product_delivery_01'),
            'serv_order': self.env.ref('product.service_order_01'),
            'serv_del': self.env.ref('product.service_delivery'),
        }
        self.sale_order_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (
                    0,
                    0,
                    {
                        'name': product.name,
                        'product_id': product.id,
                        'product_uom_qty': 2,
                        'product_uom': product.uom_id.id,
                        'price_unit': product.list_price,
                    },
                ) for (_, product) in self.products.iteritems()
            ],
            'pricelist_id': self.env.ref('product.list0').id,
        }
        self.demo_affiliate = self.env.ref(
            'website_sale_affiliate.sale_affiliate_myaffiliate'
        )
        self.demo_affiliate_2 = self.env.ref(
            'website_sale_affiliate.sale_affiliate_myotheraffiliate'
        )
        self.demo_request = self.env.ref(
            'website_sale_affiliate.sale_affiliate_request_firesale'
        )
        self.demo_company = self.env.ref('base.main_company')
