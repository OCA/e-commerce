# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    website_show_price = fields.Boolean(
        compute='_compute_website_show_price')

    def _compute_website_show_price(self):
        for rec in self:
            rec.website_show_price = (
                request.env.user.partner_id.website_show_price)
