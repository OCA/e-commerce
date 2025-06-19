# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _get_product_sort_criterias(self):
        """Extend to add more sort criterias"""
        return [
            ("website_sequence asc", self.env._("Featured")),
            ("create_date desc", self.env._("Newest Arrivals")),
            ("name asc", self.env._("Name (A-Z)")),
            ("name desc", self.env._("Name (Z-A)")),
            ("list_price asc", self.env._("Price - Low to High")),
            ("list_price desc", self.env._("Price - High to Low")),
        ]

    default_product_sort_criteria = fields.Selection(
        selection="_get_product_sort_criterias",
        string="Sort products by",
        help="Default criteria for sorting products in the shop",
        default="website_sequence asc",
        required=True,
    )
