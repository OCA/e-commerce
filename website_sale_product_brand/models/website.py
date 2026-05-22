# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if not self.has_ecommerce_access():
            return result
        if search_type in ["products", "products_only", "all"]:
            result.append(
                self.env["product.brand"]._search_get_detail(self, order, options)
            )
        return result
