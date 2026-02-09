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

    def _prepare_sale_order_values(self, partner_sudo):
        self.ensure_one()
        values = super()._prepare_sale_order_values(partner_sudo)
        sale_order_model = self.env["sale.order"].with_company(self.company_id)
        partner = partner_sudo.with_company(self.company_id)
        sale_type_id = (
            partner.sale_type.id or partner.commercial_partner_id.sale_type.id
        )
        if not sale_type_id:
            sale_type_id = sale_order_model.default_get(["type_id"]).get("type_id")
        if not sale_type_id:
            sale_type_id = sale_order_model._default_type_id().id
        if sale_type_id:
            values["type_id"] = sale_type_id
        return values
