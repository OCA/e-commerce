# Copyright 2019-Today Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    browse_only = fields.Boolean(
        help="When checked, users can no longer buy products from the webshop."
        "They can only browse the shop and see the products",
        related="website_id.browse_only",
        readonly=False,
    )
