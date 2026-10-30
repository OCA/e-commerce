# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("website_id")
    def _compute_sale_type_id(self):
        # OVERRIDE: keep the website sale type on website orders. website_sale
        # writes the partner again at checkout and on login, which would
        # otherwise recompute the type from the partner.
        res = super()._compute_sale_type_id()
        for order in self:
            website_sale_type = order.website_id.sudo().sale_type_id
            if website_sale_type:
                order.type_id = website_sale_type
        return res
