# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_variant_link_ids = fields.One2many(
        string="Product Variant Links",
        comodel_name="product.template.link",
        compute="_compute_product_link_ids",
    )

    def _compute_product_link_ids(self):
        for record in self:
            record.product_variant_link_ids = record._get_variant_links()

    def _get_variant_links(self):
        return self.product_template_link_ids.filtered_domain(
            ["|", ("left_product_id", "=", self.id), ("right_product_id", "=", self.id)]
        )
