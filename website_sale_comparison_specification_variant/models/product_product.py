# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _prepare_categories_for_display(self):
        """Same as the base method, but for non-variant-defining attributes,
        only display the values compatible with each compared product's own
        variant combination, instead of every configured value.

        Variant-defining attributes are left untouched: the base method
        already returns each product's own actual value for those, and
        filtering it through `_get_display_value_ids` would incorrectly
        turn it into every value still compatible with the product's other
        attributes, instead of the single value the product actually has.
        """
        categories = super()._prepare_categories_for_display()
        exclusions_by_template = {}
        for attributes in categories.values():
            for attribute, values_by_product in attributes.items():
                if attribute.create_variant != "no_variant":
                    continue
                for product in values_by_product:
                    ptal = product.attribute_line_ids.filtered(
                        lambda line, attribute=attribute: line.attribute_id == attribute
                    )
                    if not ptal:
                        continue
                    template = product.product_tmpl_id
                    if template.id not in exclusions_by_template:
                        exclusions_by_template[template.id] = (
                            template._get_display_attribute_exclusions()
                        )
                    values_by_product[product] = ptal._get_display_value_ids(
                        product.product_template_attribute_value_ids,
                        exclusions_by_template[template.id],
                    )
        return categories
