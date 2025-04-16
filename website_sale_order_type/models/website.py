# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def sale_get_payment_term(self, partner):
        if partner.sale_type.payment_term_id:
            return partner.sale_type.payment_term_id.id
        return super().sale_get_payment_term(partner)

    def _get_current_pricelist(self):
        partner_sudo = self.env.user.partner_id
        if partner_sudo.sale_type.pricelist_id:
            return partner_sudo.sale_type.pricelist_id.id
        return super()._get_current_pricelist()
