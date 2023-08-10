# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def sale_get_payment_term(self, partner):
        if partner.sale_type.payment_term_id:
            return partner.sale_type.payment_term_id.id
        return super().sale_get_payment_term(partner)

    def _get_current_pricelist_id(self, partner_sudo):
        if partner_sudo.sale_type.pricelist_id:
            return partner_sudo.sale_type.pricelist_id.id
        return super()._get_current_pricelist_id(partner_sudo)
