# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_template_matrix(self, **kwargs):
        matrix = super()._get_template_matrix(**kwargs)
        if not request or not request.is_frontend:
            return matrix
        # In the shop, unlike in the backend, only the published secondary units
        # can be picked and they're labeled as in the rest of the eCommerce.
        secondary_uoms = self._get_website_secondary_uoms()
        matrix["allow_uom_sell"] = self.allow_uom_sell
        matrix["secondary_units"] = [
            {"id": secondary_uom.id, "name": secondary_uom._get_website_display_name()}
            for secondary_uom in secondary_uoms
        ]
        if matrix.get("secondary_unit_id") not in secondary_uoms.ids:
            # The default unit isn't offered in the shop. Products that can't be
            # sold in their own unit still need one preselected.
            matrix["secondary_unit_id"] = (
                not self.allow_uom_sell and secondary_uoms[:1].id
            )
        return matrix
