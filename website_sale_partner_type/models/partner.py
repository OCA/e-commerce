# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    checkout_company_name = fields.Char(
        string='Checkout Company Name')
