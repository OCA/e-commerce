# Copyright 2019-Today Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):

    _inherit = "website"

    enable_browse_mode = fields.Boolean(
        default=False,
        help="When checked, users can no longer buy products from the webshop."
        "They can only browse the shop and see the products",
    )
