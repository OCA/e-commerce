# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_attribute_exclusions(
        self, parent_combination=None, parent_name=None, combination_ids=None
    ):
        result = super()._get_attribute_exclusions(
            parent_combination=parent_combination,
            parent_name=parent_name,
            combination_ids=combination_ids,
        )
        no_variant_ptav_ids = set(
            self.attribute_line_ids.filtered(
                lambda line: line.attribute_id.create_variant == "no_variant"
            ).product_template_value_ids.ids
        )
        if not no_variant_ptav_ids:
            return result

        result["exclusions"] = {
            ptav_id: (
                []
                if ptav_id in no_variant_ptav_ids
                else [
                    excluded_id
                    for excluded_id in excluded_ids
                    if excluded_id not in no_variant_ptav_ids
                ]
            )
            for ptav_id, excluded_ids in result["exclusions"].items()
        }
        result["parent_exclusions"] = {
            parent_ptav_id: [
                excluded_id
                for excluded_id in excluded_ids
                if excluded_id not in no_variant_ptav_ids
            ]
            for parent_ptav_id, excluded_ids in result["parent_exclusions"].items()
        }
        result["mapped_attribute_names"] = {
            ptav_id: name
            for ptav_id, name in result["mapped_attribute_names"].items()
            if ptav_id not in no_variant_ptav_ids
        }
        return result

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        uom_id=False,
        only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
        )
        if combination_info.get("is_combination_possible"):
            return combination_info
        # Since no_variant attributes are never shown to the shopper (see the
        # website_sale.variants override), they can never be submitted or
        # corrected from the website, so they must not be able to block Add
        # to Cart either: a missing or template-picked no_variant value would
        # otherwise fail the exact-attribute-match/exclusion check in
        # `_is_combination_possible` with no way for the shopper to fix it.
        resolved_combination = (
            combination_info.get("combination")
            or self.env["product.template.attribute.value"]
        )
        combination_info["is_combination_possible"] = self._is_combination_possible(
            combination=resolved_combination._without_no_variant_attributes(),
            ignore_no_variant=True,
        )
        return combination_info
