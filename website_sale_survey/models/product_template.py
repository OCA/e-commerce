# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    survey_id = fields.Many2one(
        "survey.survey",
        string="Survey",
        domain=[("is_closed", "=", False)],
        ondelete="restrict",
        help="Ask buyers to answer this survey before buying.",
    )
