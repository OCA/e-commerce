# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    affiliate_request_id = fields.Many2one(
        "sale.affiliate.request",
        string="Affiliate request",
        help="Affiliate request associated with sale order",
    )

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        AffiliateRequest = self.env["sale.affiliate.request"]
        res.affiliate_request_id = AffiliateRequest.current_qualified()
        return res
