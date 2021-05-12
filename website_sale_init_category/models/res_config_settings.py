# Copyright 2021 Manuel Calero <https://xtendoo.es/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    init_category_id = fields.Many2one(
        "product.public.category",
        string="Init Category",
        related="website_id.init_category_id",
        readonly=False,
    )
