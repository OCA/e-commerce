# Copyright 2020 Tecnativa - Jairo Llopis
# Copyright 2021 Tecnativa - Pedro M. Baeza
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
    website_name = fields.Char(
        string="Name in e-commerce",
        help="The name of the download that will be displayed on the e-commerce "
        "product page. If not filled, the filename will be shown by default.",
    )
