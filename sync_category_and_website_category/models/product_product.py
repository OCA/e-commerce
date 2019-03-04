# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models
from ..sync_utils import syncronize


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        new_pp = False
        # if somehow we are changing the public category and this code is
        # active just pop it, this module only considers that internal
        # categories may be changed.
        if self.env.context.get('no_sync'):
            new_pt = super(ProductProduct, self).write(vals)
            return new_pt
        vals = syncronize(self.env, vals)
        new_pp = super(ProductProduct, self).create(vals)
        return new_pp

    @api.multi
    def write(self, vals):
        written_product = False
        # as allways you can never change directly public cat
        if self.env.context.get('no_sync'):
            written_product = super(ProductProduct, self).write(vals)
            return written_product
        for this in self:
            sync_vals = syncronize(
                self.env, vals, this.categ_id, this.categ_ids)
            written_product = super(ProductProduct, this).write(sync_vals)
        return written_product
