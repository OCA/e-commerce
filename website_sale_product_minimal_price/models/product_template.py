# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_first_possible_combination(
        self, parent_combination=None, necessary_values=None
    ):
        """
        Get the cheaper product combination for the product for website view.
        We only take into account attributes that generate variants and
        products with more than one variant.
        """
        combination = super()._get_first_possible_combination(
            parent_combination=parent_combination, necessary_values=necessary_values
        )
        if self.env.context.get("website_id") and self.product_variant_count > 1:
            ptav_obj = self.env["product.template.attribute.value"]
            ptav = self.product_variant_ids.sorted(
                key=lambda p: p._get_combination_info_variant().get("price")
            )[:1].product_template_attribute_value_ids
            cheaper_combination = ptav_obj.search(
                [
                    ("product_tmpl_id", "=", self.id),
                    (
                        "product_attribute_value_id",
                        "in",
                        ptav.product_attribute_value_id.ids,
                    ),
                ]
            )
            variant_combination = combination.filtered(
                lambda x: x.attribute_id.create_variant == "always"
            )
            combination_returned = cheaper_combination + (
                combination - variant_combination
            )
            # Keep order to avoid This combination does not exist message
            return combination_returned.sorted(lambda x: x.attribute_id.sequence)
        return combination
