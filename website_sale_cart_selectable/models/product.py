# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_btn_addtocart_published = fields.Boolean(
        string='Display "Add to Cart" Button', copy=False, default=True
    )
