# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _prepare_sale_order_values(self, partner_sudo):
        """Set the company as customer and the contact as sale contact."""
        values = super()._prepare_sale_order_values(partner_sudo)
        company_sudo = partner_sudo._get_sale_contact_company()
        if company_sudo:
            values["partner_id"] = company_sudo.id
            values["sale_contact_partner_id"] = partner_sudo.id
        return values
