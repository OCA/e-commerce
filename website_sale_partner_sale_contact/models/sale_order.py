# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_address(self, partner_id, fnames=None):
        """Remap only the customer to the company; keep entered addresses."""
        if fnames and "partner_id" in fnames:
            partner = self.env["res.partner"].browse(partner_id)
            company = partner._get_sale_contact_company()
            if company:
                address_fnames = [name for name in fnames if name != "partner_id"]
                res = super()._update_address(company.id, ["partner_id"])
                if address_fnames:
                    # Re-apply entered addresses; the customer change reset them.
                    res = super()._update_address(partner_id, address_fnames)
                self.sale_contact_partner_id = partner
                return res
        return super()._update_address(partner_id, fnames)
