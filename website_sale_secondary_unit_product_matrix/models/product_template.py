# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_template_matrix(self, **kwargs):
        matrix = super()._get_template_matrix(**kwargs)
        matrix["allow_uom_sell"] = self.allow_uom_sell
        return matrix
