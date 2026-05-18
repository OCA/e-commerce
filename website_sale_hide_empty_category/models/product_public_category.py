# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    has_product_recursive = fields.Boolean(
        string="This category or one of its children has products",
        compute="_compute_has_product_recursive",
        recursive=True,
    )

    @api.depends("product_tmpl_ids", "child_id.has_product_recursive")
    @api.depends_context("website_id")
    def _compute_has_product_recursive(self):
        for category in self:
            website = self.env["website"].get_current_website()
            website_domain = website.sale_product_domain()
            has_products = bool(
                category.product_tmpl_ids.filtered_domain(website_domain)
            )
            category.has_product_recursive = has_products or any(
                child.has_product_recursive for child in category.child_id
            )
