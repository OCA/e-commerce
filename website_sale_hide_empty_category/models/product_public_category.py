# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    has_product_recursive = fields.Boolean(
        string="This category or one of its children has products",
        compute="_compute_has_product_recursive",
    )

    count_product_recursive = fields.Integer(
        string="Number of products in this category or one of its children",
        compute="_compute_has_product_recursive",
    )

    @api.depends("product_tmpl_ids", "child_id.has_product_recursive")
    def _compute_has_product_recursive(self):
        for category in self:
            product_count = len(category.product_tmpl_ids) + sum(
                child.has_product_recursive for child in category.child_id
            )
            category.count_product_recursive = product_count
            category.has_product_recursive = bool(product_count)
