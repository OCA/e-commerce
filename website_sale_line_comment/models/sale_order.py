# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    website_note = fields.Text("Website Note")
