# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'  # pylint: disable=R7980

    ttr_impa1 = fields.Char(string='Impa1', ttr_mag_attribute=True)
    ttr_issa = fields.Char(string='ISSA code', ttr_mag_attribute=True)
