# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    # This module relies on the M2M relation built from `product.template` to
    # `product.public.category` named `public_categ_ids`
    product_ids = fields.Many2many(
        comodel_name='product.template',
        string='Products',
        relation='product_public_category_product_template_rel',
        column1='product_public_category_id',
        column2='product_template_id',
    )

    has_product_recursive = fields.Boolean(
        string='This category or one of its children has products',
        compute='_compute_has_product_recursive'
    )

    @api.depends('product_ids', 'child_id.has_product_recursive')
    def _compute_has_product_recursive(self):
        for category in self:
            category.has_product_recursive = \
                bool(category.product_ids or any((child.has_product_recursive
                                                  for child in
                                                  category.child_id)))
