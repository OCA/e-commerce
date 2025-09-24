# Copyright 2025 Tecnativa - Pilar Vargas
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(self, force_create=False, update_pricelist=False):
        # This method manages the entire flow of an order on the website, from adding a
        # product to the cart to payment. The active order is retrieved by calling
        # this method.
        # This method is also called from checkout to manage addresses.
        origin_partner = self.env["res.partner"]
        portal_order_id = request.session.get("portal_order_id", False)
        portal_access_token = request.session.get("portal_access_token", False)
        sale_order_id = request.session.get("sale_order_id")
        # In the parent method, the data of an order is changed to the active user.
        # If the address of a quote is being edited from the portal, the data of the
        # quote being edited must be retrieved so that the partner is not modified and
        # therefore manages its own addresses.
        if not (portal_order_id and portal_access_token and sale_order_id):
            return super().sale_get_order(
                force_create=force_create, update_pricelist=update_pricelist
            )
        origin_so = self.env["sale.order"].sudo().browse(sale_order_id).exists()
        origin_partner = origin_so.partner_id
        previous_fiscal_position = origin_so.fiscal_position_id
        previous_pricelist = origin_so.pricelist_id
        previous_payment_term = origin_so.payment_term_id
        sale_order_sudo = super().sale_get_order(
            force_create=force_create, update_pricelist=update_pricelist
        )
        if origin_partner and sale_order_sudo.partner_id != origin_partner:
            sale_order_sudo.write(
                {
                    "partner_id": origin_partner.id,
                    "partner_invoice_id": origin_partner.id,
                    "payment_term_id": previous_payment_term,
                    "pricelist_id": previous_pricelist,
                }
            )
        if sale_order_sudo.fiscal_position_id != previous_fiscal_position:
            sale_order_sudo.order_line._compute_tax_id()
        if sale_order_sudo.pricelist_id != previous_pricelist:
            sale_order_sudo._recompute_prices()
        return sale_order_sudo
