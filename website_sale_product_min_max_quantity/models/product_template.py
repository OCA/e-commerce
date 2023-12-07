# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# Copyright 2024 Binhex - Adasat Torres de León <a.torres@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_sale_min_qty = fields.Float(
        string="Min. quantity",
        default=1.0,
        help="Minimum quantity that can be added to the cart.",
    )

    website_sale_max_qty = fields.Float(
        string="Max. quantity",
        default=9999.0,
        help="Maximum quantity that can be added to the cart.",
    )
