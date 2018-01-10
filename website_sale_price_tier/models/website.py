# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    show_implicit_price_tier = fields.Boolean(
        string='Implicit Price Tier',
    )
