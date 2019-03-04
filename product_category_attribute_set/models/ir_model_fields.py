# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    ttr_mag_attribute = fields.Boolean(
        string="Technotrading Magento Attribute",
        default=False
    )
