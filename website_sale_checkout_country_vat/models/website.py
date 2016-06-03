# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import fields, models


class Website(models.Model):
    _inherit = 'website'

    vat_code_id = fields.Many2one(
        comodel_name='res.country', string="Default VAT Code", size=2)
