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

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        affiliate_request = self.env["sale.affiliate.request"].current_qualified()
        if affiliate_request:
            res.update({"affiliate_request_id": affiliate_request.id})
        return res
