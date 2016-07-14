# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields


class ProductPricelistVersion(models.Model):
    _name = 'product.pricelist.version'
    _inherit = 'product.pricelist.version'

    effective_date_start = fields.Datetime(
        string='Google Shopping date start')
    effective_date_end = fields.Datetime(
        string='Google Shopping date end')
