# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_and_cache_current_cart(self):
        sale_order_sudo = super()._get_and_cache_current_cart()
        # Skip-payment quotations have been "handed off" to the salesperson;
        # they must not be resurrected as the active cart, even though they
        # remain in draft state.
        if sale_order_sudo and sale_order_sudo.is_skip_payment_quotation:
            self.sale_reset()
            return self.env["sale.order"].sudo()
        return sale_order_sudo
