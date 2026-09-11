# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_website_secondary_uoms(self):
        """Secondary units that can be picked by a customer in the shop."""
        self.ensure_one()
        return self.secondary_uom_ids._filter_website_published()
