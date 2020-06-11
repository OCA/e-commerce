# Copyright 2020 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    attached_in_product_tmpl_ids = fields.Many2many(
        string="Attached in products",
        comodel_name="product.template",
        help="Attachment publicly downladable from eCommerce pages "
             "in these product templates.",
    )
