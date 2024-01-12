# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    b2b_information = fields.Html(translate=True)
    b2c_information = fields.Html(translate=True)
