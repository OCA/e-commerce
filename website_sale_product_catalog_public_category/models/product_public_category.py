# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    @api.depends_context("hierarchical_naming")
    def _compute_display_name(self):
        # The search panel asks for names without their parents, as
        # product.category supports, to show them in its tree
        if self.env.context.get("hierarchical_naming", True):
            return super()._compute_display_name()
        for category in self:
            category.display_name = category.name
