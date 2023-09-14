# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductAlias(models.Model):
    _name = "product.alias"

    product_tmpl_id = fields.Many2one(
        "product.template",
        required=True,
    )

    name = fields.Char(
        string="Name",
        required=True,
    )

    attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Attribute Values",
        domain="[('id', 'in', available_attribute_value_ids)]",
        required=True,
    )

    available_attribute_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Available Attributes",
        compute="_compute_available_attribute",
    )

    @api.depends("product_tmpl_id")
    def _compute_available_attribute(self):
        for rec in self:
            if self.env.context.get("default_product_tmpl_id"):
                tmpl = self.env["product.template"].search(
                    [("id", "=", self.env.context.get("default_product_tmpl_id"))],
                    limit=1,
                )
            else:
                tmpl = self.product_tmpl_id
            rec.available_attribute_value_ids = [
                (6, 0, tmpl.attribute_line_ids.value_ids._origin.ids)
            ]
