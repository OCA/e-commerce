# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAlias(models.Model):
    _inherit = "product.alias"

    product_alias_link_ids = fields.One2many(
        string="Product Alias Links",
        comodel_name="product.template.link",
        compute="_compute_product_link_ids",
    )

    def _compute_product_link_ids(self):
        for record in self:
            record.product_alias_link_ids = record._get_alias_links()

    def _get_alias_links(self):
        return self.product_alias_link_ids.filtered_domain(
            [
                "|",
                ("left_product_alias_id", "=", self.id),
                ("right_product_alias_id", "=", self.id),
            ]
        )
