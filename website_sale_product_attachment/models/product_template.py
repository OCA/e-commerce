# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    attachments = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachments',
        domain=[
            ('public', '=', True),
            ('res_model', '=', 'product.template'),
        ]
    )
