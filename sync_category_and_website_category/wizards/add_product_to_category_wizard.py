# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AddProductToCategoryWizard(models.TransientModel):

    _name = "add_prd_wiz"
    _description = "wizard to add product to category"

    @api.model
    def default_get(self, fields_list):
        result = super(AddProductToCategoryWizard, self).default_get(
            fields_list=fields_list
        )
        result["category_id"] = self.env.context.get("active_id", False)
        return result

    @api.multi
    def add_product_to_internal_category(self):
        product = self.product_id
        if self.category_type == 'main_category':
            return product.write({'categ_id': self.category_id.id})
        return product.write({'categ_ids': [(4, self.category_id.id, 0)]})

    product_id = fields.Many2one(
        "product.product",
        required=True
    )
    category_id = fields.Many2one('product.category', required=True)
    category_type = fields.Selection(
        [('main_category', 'Set as Main Category'),
         ('extra_category', 'Add to extra Categories')],
        default='main_category',
        required=True
    )
    current_main_cat_id = fields.Many2one(
        'product.category',
        related='product_id.product_tmpl_id.categ_id'
        )
    current_extra_cat_ids = fields.Many2many(
        'product.category',
        related='product_id.product_tmpl_id.categ_ids'
        )
