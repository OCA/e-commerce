# Copyright 2021 Manuel Calero <https://xtendoo.es/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    init_category_id = fields.Many2one(
        "product.public.category",
        string="Init Category",
        help="This field holds the e-commerce init category.",
    )
