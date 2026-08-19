# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    def _get_display_value_ids(self, combination, exclusions=None):
        self.ensure_one()
        if not combination:
            return self.value_ids
        if self.attribute_id.create_variant != "no_variant":
            # There is no candidate set to narrow down here: `combination`
            # already carries the one value selected for this line, exactly
            # like `ProductProduct._prepare_categories_for_display` shows
            # each compared product's own actual value.
            return (
                self.product_template_value_ids & combination
            ).product_attribute_value_id
        if exclusions is None:
            exclusions = self.product_tmpl_id._get_display_attribute_exclusions()
        other_ids = set(combination.ids) - set(self.product_template_value_ids.ids)
        displayed_value_ids = set()
        for ptav in self.product_template_value_ids:
            conflicts = any(
                other_id in exclusions.get(ptav.id, []) for other_id in other_ids
            )
            if not conflicts:
                displayed_value_ids.add(ptav.product_attribute_value_id.id)
        return self.env["product.attribute.value"].browse(displayed_value_ids).exists()
