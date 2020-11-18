# Copyright 2020 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        values = super()._prepare_sale_order_values(partner, pricelist)
        values[
            "payment_mode_id"
        ] = partner.commercial_partner_id.customer_payment_mode_id.id
        return values
