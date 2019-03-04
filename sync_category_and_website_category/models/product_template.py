# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models
from ..sync_utils import syncronize


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        new_pt = False
        # if somehow we are changing the public category and this code is
        # active just pop it, this module only considers that internal
        # categories may be changed.
        if self.env.context.get('no_sync'):
            new_pt = super(ProductTemplate, self).create(vals)
            return new_pt
        sync_vals = syncronize(self.env, vals)
        new_pt = super(ProductTemplate, self).create(sync_vals)
        return new_pt

    @api.multi
    def write(self, vals):
        written_product = False
        if self.env.context.get('no_sync'):
            written_product = super(ProductTemplate, self).write(vals)
            return written_product
        for this in self:
            sync_vals = syncronize(
                self.env, vals, this.categ_id, this.categ_ids)
            written_product = super(ProductTemplate, this).write(sync_vals)
        return written_product
