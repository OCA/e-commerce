# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    alias_id = fields.Many2one(
        "product.alias", "Alias", compute="_compute_alias_id", store=True
    )

    def _get_matching_alias(self):
        match = self.env["product.alias"]
        values = self.product_template_attribute_value_ids.product_attribute_value_id
        for alias in self.product_alias_ids:
            attrs = alias.attribute_value_ids.attribute_id
            variant_values = values.filtered(lambda s: s.attribute_id in attrs)
            if not (variant_values - alias.attribute_value_ids):
                match |= alias
        if len(match) > 1:
            raise UserError(
                _(
                    "Wrong alias attribute value configuration"
                    "The variant %(variant)s match too many aliases %(aliases)s",
                )
                % dict(
                    variant=self.display_name,
                    aliases=match.mapped("name"),
                )
            )
        return match

    @api.depends("product_alias_ids.attribute_value_ids")
    def _compute_alias_id(self):
        for record in self:
            record.alias_id = record._get_matching_alias()
