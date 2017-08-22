# -*- coding: utf-8 -*-
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # HACK Redefine computation or we cannot override it
    lst_price = fields.Float(compute="_product_lst_price")
    price_extra = fields.Float(compute="_get_price_extra")

    @api.multi
    def _product_lst_price(self):
        # Patch context to avoid double computing taxes
        self_b2b = self.with_context(b2c_prices=False)
        result = self.env["product.template"]._price_b2c_wrapper(
            self_b2b,
            super(ProductProduct, self_b2b)
            ._product_lst_price("lst_price", None),
        )
        for one in self:
            one.lst_price = result[one.id]

    @api.multi
    def _get_price_extra(self):
        result = self.env["product.template"]._price_b2c_wrapper(
            self,
            super(ProductProduct, self)._get_price_extra("price_extra", None),
        )
        for one in self:
            one.price_extra = result[one.id]
