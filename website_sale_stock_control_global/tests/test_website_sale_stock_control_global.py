# -*- coding: utf-8 -*-
# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests import common


class WebsiteSaleStockControlGlobalCase(common.SavepointCase):
    def setUp(cls):
        super(WebsiteSaleStockControlGlobalCase, cls).setUp()
        cls.company2 = cls.env['res.company'].create({
            'name': 'company2',
        })
        cls.product_tmpl = cls.env['product.template'].create({
            'name': 'Test template',
            'type': 'product',
        })

    def test_stock_global(self):
        vals = {
            'product_id': self.product_tmpl.product_variant_ids.id,
            'product_tmpl_id': self.product_tmpl.id,
        }
        location_company1 = self.env['stock.location'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('usage', '=', 'internal'),
        ])[:1]
        vals.update({
            'location_id': location_company1.id,
            'new_quantity': 5.0,
        })
        wiz_company1 = self.env['stock.change.product.qty'].create(vals)
        wiz_company1.change_product_qty()
        self.assertEqual(self.product_tmpl.website_qty_available, 5.0)

        self.env.user.company_id = self.company2
        self.env['stock.warehouse'].create({
            'name': 'Wharehouse 2',
            'code': 'WH2',
            'company_id': self.company2.id,
        })
        location_company2 = self.env['stock.location'].search([
            ('company_id', '=', self.company2.id),
            ('usage', '=', 'internal'),
        ])[:1]
        vals.update({
            'location_id': location_company2.id,
            'new_quantity': 7.0,
        })
        wiz_company2 = self.env['stock.change.product.qty'].create(vals)
        wiz_company2.change_product_qty()
        self.assertEqual(self.product_tmpl.website_qty_available, 12.0)
