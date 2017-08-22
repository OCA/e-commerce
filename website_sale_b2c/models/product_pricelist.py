# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def price_rule_get_multi(self, products_by_qty_by_partner):
        res = super(ProductPricelist, self).price_rule_get_multi(
            products_by_qty_by_partner)
        for product, qty, partner in products_by_qty_by_partner:
            for pricelist, (price, min_qty) in res[product.id].iteritems():
                wrapped = product.env['product.template']._price_b2c_wrapper(
                    product,
                    {product.id: price},
                )
                res[product.id][pricelist] = (wrapped[product.id], min_qty)
        return res
