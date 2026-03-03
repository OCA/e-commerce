# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _prepare_sale_order_values(self, partner_sudo):
        self.ensure_one()
        so_data = super()._prepare_sale_order_values(partner_sudo)

        sale_type = partner_sudo.sale_type
        if sale_type:
            so_data["type_id"] = sale_type.id
            if sale_type.payment_term_id:
                so_data["payment_term_id"] = sale_type.payment_term_id.id
        return so_data

    def get_pricelist_available(self, show_visible=False):
        website = self.with_company(self.company_id)
        partner_sudo = website.env.user.partner_id
        pricelists = super().get_pricelist_available(show_visible)
        if partner_sudo.sale_type.pricelist_id:
            pricelists = pricelists.filtered(
                lambda p: p.id == partner_sudo.sale_type.pricelist_id.id
            )
        return pricelists
