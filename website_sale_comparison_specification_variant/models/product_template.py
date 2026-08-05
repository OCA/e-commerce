# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_display_attribute_exclusions(self):
        self.ensure_one()
        return self._complete_inverse_exclusions(self._get_own_attribute_exclusions())

    def _get_specs_render_context(self, combination):
        """Return the qweb rendering context for the specs tables matching
        `combination` (recordset of `product.template.attribute.value`), or
        `None` if no line has more than one value to filter.
        """
        self.ensure_one()
        has_filterable_line = any(
            len(ptal.value_ids) > 1
            for ptal in self.valid_product_template_attribute_line_ids
        )
        if not has_filterable_line:
            return None
        ptals = self.valid_product_template_attribute_line_ids
        attrib_categories = ptals._prepare_categories_for_display_in_specs_table()
        if not attrib_categories:
            return None
        return {
            "attrib_categories": attrib_categories,
            "combination": combination,
            "attribute_exclusions": self._get_display_attribute_exclusions(),
        }

    def _get_specs_table_html(self, combination):
        """Render the specs table content for the given `combination`
        (recordset of `product.template.attribute.value`), so it can be
        refreshed client-side when the customer changes variant.

        Called only from the `/website_sale/get_combination_info` controller
        """
        self.ensure_one()
        render_context = self._get_specs_render_context(combination)
        if render_context is None:
            return None
        return self.env["ir.qweb"]._render(
            "website_sale_comparison_specification_variant"
            ".product_specifications_content",
            render_context,
        )

    def _get_specs_accordion_html(self, combination):
        """Render the specs accordion content for the given `combination`
        (recordset of `product.template.attribute.value`), so it can be
        refreshed client-side when the customer changes variant, without
        disturbing the accordion's open/collapsed state.

        Called only from the `/website_sale/get_combination_info` controller
        """
        self.ensure_one()
        render_context = self._get_specs_render_context(combination)
        if render_context is None:
            return None
        return self.env["ir.qweb"]._render(
            "website_sale_comparison_specification_variant"
            ".product_specifications_accordion_content",
            render_context,
        )
