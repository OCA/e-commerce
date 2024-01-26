#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager, nullcontext

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCartPrint(WebsiteSale):
    @contextmanager
    def _cart_print_patch_session_order(self):
        """Set the current sale order as the 'last_order' in session.

        This is needed because super's print_saleorder prints that order,
        and it is not saved as the 'last_order' until it is confirmed.
        """
        sale_order_id = request.session.get("sale_last_order_id")
        order_sudo = request.website.sale_get_order()
        request.session["sale_last_order_id"] = order_sudo.id

        yield

        if sale_order_id is not None:
            # Restore the previous stored order
            request.session["sale_last_order_id"] = sale_order_id
        else:
            # If there was no order, delete the key
            del request.session["sale_last_order_id"]

    @http.route()
    def print_saleorder(self, cart_print=None, **kwargs):
        patch_session_order_cm = (
            self._cart_print_patch_session_order()
            if cart_print is not None
            else nullcontext()
        )
        with patch_session_order_cm:
            return super().print_saleorder(cart_print=cart_print, **kwargs)
