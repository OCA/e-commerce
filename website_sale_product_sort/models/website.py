# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _get_product_sort_criterias(self):
        """Extend to add more sort criterias"""
        return [
            ('website_sequence desc', _('Relevance')),
            ('list_price desc', _('Catalog price: High to Low')),
            ('list_price asc', _('Catalog price: Low to High')),
            ('name asc', _('Name - A to Z')),
            ('name desc', _('Name - Z to A')),
        ]

    default_product_sort_criteria = fields.Selection(
        selection='_get_product_sort_criterias',
        string="Sort products by",
        help="Default criteria for sorting products in the shop",
        default='website_sequence desc',
        required=True,
    )
