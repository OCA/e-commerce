# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    @http.route()
    def portal_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
        **kw,
    ):
        for key in ("portal_order_id", "portal_access_token", "sale_order_id"):
            request.session.pop(key, None)
        return super().portal_order_page(
            order_id=order_id,
            report_type=report_type,
            access_token=access_token,
            message=message,
            download=download,
            downpayment=downpayment,
            **kw,
        )
