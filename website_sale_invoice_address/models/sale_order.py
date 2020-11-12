# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        """ Catch the context from the website write so we ensure the correct
        invoice partner as we would do in backend"""
        override_invoice_partner = self.env.context.get(
            "override_partner_invoice_id")
        partner_obj = self.env["res.partner"]
        if override_invoice_partner and "partner_invoice_id" in vals:
            partner = vals.get("partner_id", self.partner_id.id)
            if partner:
                partner = partner_obj.browse(partner)
                partner_invoice_id = partner.address_get(
                    ["invoice"]).get("invoice")
                vals["partner_invoice_id"] = partner_obj.browse(
                    partner_invoice_id).id
        return super().write(vals)
