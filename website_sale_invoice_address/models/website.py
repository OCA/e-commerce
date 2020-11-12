# Copyright 2020 David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(
        self,
        force_create=False,
        code=None,
        update_pricelist=False,
        force_pricelist=False,
    ):
        """Odoo commit 6e69de67071f2618e00856a74716d861b7f47391 breaks the old
        flow that puts the invoice partner of the commercial entity. In a B2B
        environment this is quite necessary. Well catch the context in
        `sale.order`"""
        self_ctx = self.with_context(override_partner_invoice_id=True)
        return super(Website, self_ctx).sale_get_order(
            force_create=force_create,
            code=code,
            update_pricelist=update_pricelist,
            force_pricelist=force_pricelist,
        )

    def _prepare_sale_order_values(self, partner, pricelist):
        """Ensure correct invoice partner"""
        vals = super()._prepare_sale_order_values(partner, pricelist)
        # Recover v11 partner invoice behavior
        partner_invoice_id = partner.address_get(["invoice"]).get("invoice")
        vals.update(
            {
                "partner_invoice_id": partner_invoice_id,
            }
        )
        return vals
