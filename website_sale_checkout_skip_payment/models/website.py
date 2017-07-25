# -*- coding: utf-8 -*-
# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, fields, models
from openerp.http import request


class Website(models.Model):
    _inherit = "website"

    checkout_skip_payment = fields.Boolean(
        compute='_compute_checkout_skip_payment')

    @api.multi
    def _compute_checkout_skip_payment(self):
        for rec in self:
            if request.session.uid:
                partner = self.env['res.users'].browse(
                    request.session.uid).partner_id
                if partner.skip_website_checkout_payment:
                    rec.checkout_skip_payment = True
