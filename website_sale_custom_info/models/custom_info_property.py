# -*- coding: utf-8 -*-
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from openerp import fields, models


class CustomInfoProperty(models.Model):
    _inherit = "custom.info.property"

    product_public_filter = fields.Selection(
        selection=[("quick", "Quick"), ("advanced", "Advanced")],
        help="Enables this property as a search filter in the website shop. "
             "'Quick' displays it in the left panel if available, and "
             "'Advanced' displays it in an advanced filters modal. "
             "This only works when the model is 'product.template'.",
    )
