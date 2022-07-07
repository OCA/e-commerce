# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError, MissingError
from odoo.http import request, route

from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortalTierValidation(CustomerPortal):
    @route(
        ["/my/orders/<int:order_id>/validate"], type="http", auth="public", website=True
    )
    def portal_quote_request_validation(self, order_id, access_token=None):
        access_token = access_token or request.httprequest.args.get("access_token")
        try:
            order_sudo = self._document_check_access(
                "sale.order", order_id, access_token=access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        query_string = False
        if not order_sudo.need_validation:
            query_string = "&message=cant_validate"
        else:
            order_sudo.with_context(send_email_customer=True).request_validation()
        return request.redirect(order_sudo.get_portal_url(query_string=query_string))
