# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_sale_min_qty = fields.Float(
        string="Cantidad mínima",
        default=1.0,
        help="Cantidad mínima que se puede añadir al carrito",
    )

    website_sale_max_qty = fields.Float(
        string="Cantidad máxima",
        default=9999.0,
        help="Cantidad máxima que se puede añadir al carrito",
    )
