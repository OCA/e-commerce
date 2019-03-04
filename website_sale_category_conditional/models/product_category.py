# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ProductCategory(models.Model):

    def get_all_parents(self):
        self.ensure_one()
        res = self
        if self.parent_id:
            res += self.parent_id + self.parent_id.get_all_parents()
        return res

    def get_all_children(self):
        self.ensure_one()
        res = self
        for child in self.child_id:
            res += child + child.get_all_children()
        return res

    _inherit = "product.category"

    published = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        new_category = super(ProductCategory, self).create(vals)
        if self.env.context.get('recursion_done'):
            return new_category
        # propagate to all parents recursivley all "on website"
        if 'published' in vals.keys() and vals['published']:
            # make "published" the entire parent tree if false skip it
            parents = new_category.get_all_parents()
            parents.with_context(recursion_done=True).write(
                {'published': vals['published']}
            )
        return new_category

    @api.multi
    def write(self, vals):
        written_category = super(ProductCategory, self).write(vals)
        if self.env.context.get('recursion_done'):
            return written_category
        if 'published' in vals.keys():
            # if i set to true, make all parents true
            if vals['published']:
                for this in self:
                    # make "on website" the entire parent tree if false skip it
                    parents = self.env['product.category']
                    parents = this.get_all_parents()
                    if parents:
                        parents.with_context(recursion_done=True).write(
                            {'published': vals['published']})
                return written_category
            # if i set to false, make all children false
            for this in self:
                children = self.env['product.category']
                children = this.get_all_children()
                if children:
                    children.with_context(recursion_done=True).write(
                        {'published': vals['published']})
        return written_category
