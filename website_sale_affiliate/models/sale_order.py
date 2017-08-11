# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    affiliate_request_id = fields.Many2one(
        'sale.affiliate.request',
        string='Affiliate request',
        help='Affiliate request associated with sale order',
    )

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        affiliate = self.env['sale.affiliate'].find_from_session()
        try:
            res.affiliate_request_id = affiliate.get_request()
        except AttributeError:
            pass
        return res
