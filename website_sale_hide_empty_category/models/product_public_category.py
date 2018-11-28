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

    has_products_recurcive = fields.Boolean(
        string='This catégory or one of its children has product',
        compute='_has_products_recurcive'
    )

    @api.depends('product_ids', 'child_id.has_products_recurcive')
    def _has_products_recurcive(self):
        for category in self:
            category.has_products_recurcive = \
                bool(category.product_ids or any((child.has_products_recurcive
                                                  for child in
                                                  category.child_id)))

