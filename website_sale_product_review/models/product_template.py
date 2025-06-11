# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    review_count = fields.Integer(compute="_compute_review_count")

    def _compute_review_count(self):
        for product in self:
            product.review_count = self.env["product.review"].search_count(
                [("product_id", "=", product.id)]
            )
