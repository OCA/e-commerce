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

    def _get_possible_variant_combinations(self, parent_combination=None):
        """Same as `_get_possible_combinations`, but only on the
        variant-defining attribute lines.

        The no_variant lines are never shown to the shopper (see the
        website_sale.variants override), so their values must not make an
        otherwise sellable variant impossible: e.g. an informational attribute
        whose only value is excluded for some variants would otherwise leave
        those variants without any possible combination.
        """
        self.ensure_one()
        valid_lines = self.valid_product_template_attribute_line_ids
        attribute_lines = valid_lines._without_no_variant_attributes()
        if not attribute_lines:
            combination = self.env["product.template.attribute.value"]
            if self._is_combination_possible(
                combination, parent_combination, ignore_no_variant=True
            ):
                yield combination
            return
        values_per_line = [
            line.product_template_value_ids._only_active()
            if line.attribute_id.display_type != "multi"
            else self.env["product.template.attribute.value"]
            for line in attribute_lines
        ]
        for combination in self._cartesian_product(values_per_line, parent_combination):
            if self._is_combination_possible(
                combination, parent_combination, ignore_no_variant=True
            ):
                yield combination

    def _is_add_to_cart_possible(self, parent_combination=None):
        # OVERRIDE: the standard check requires a possible combination that
        # includes a value for every no_variant line, so hidden informational
        # values excluded for some variants can make the whole product unsellable
        # ("This product has no valid combination"). Only the variant-defining
        # lines can be chosen by the shopper, so only those must be possible.
        if super()._is_add_to_cart_possible(parent_combination=parent_combination):
            return True
        if not self.active or not self._can_be_added_to_cart():
            return False
        return (
            next(self._get_possible_variant_combinations(parent_combination), False)
            is not False
        )

    def _get_first_possible_combination(
        self, parent_combination=None, necessary_values=None
    ):
        # OVERRIDE: the standard first combination includes a value for every
        # no_variant line, so it is empty when hidden informational values
        # exclude every variant, leaving the product page, the shop grid
        # (`_get_first_possible_variant_id`) and the product configurator
        # without any variant to start from. Fall back on the first
        # variant-defining combination in that case, see
        # `_get_possible_variant_combinations`. The fallback cannot honor
        # `necessary_values`, so it only applies when none are required.
        combination = super()._get_first_possible_combination(
            parent_combination=parent_combination, necessary_values=necessary_values
        )
        if combination or necessary_values:
            return combination
        return next(
            self._get_possible_variant_combinations(parent_combination), combination
        )

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
