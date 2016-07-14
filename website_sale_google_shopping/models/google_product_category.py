# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields


class GoogleProductCategory(models.Model):
    _name = 'google_product_category'
    _description = 'Google product category'

    name = fields.Char(
        string='Name',
        required=True)
    google_id = fields.Char(
        string='Google Id',
        required=True)

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'The Name must be unique!'),
        ('google_id_unique',
         'unique (google_id)', 'The Google Id must be unique!'),
    ]
