# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    use_osc = fields.Boolean(
        string='Use OSC',
        default=True,)
