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
        website = self.env["website"].get_current_website()
        product_domain = website.sale_product_domain()
        categories_with_products = self.search(
            [
                ("website_id", "in", [False, website.id]),
                ("product_tmpl_ids", "any", product_domain),
            ]
        )
        used_category_ids = set()
        for category in categories_with_products:
            used_category_ids.update(
                int(category_id)
                for category_id in category.parent_path.split("/")
                if category_id
            )
        categories = self.search(website.website_domain()) | self
        self.env.cache.update_raw(
            categories,
            self._fields["has_product_recursive"],
            [category.id in used_category_ids for category in categories],
        )
