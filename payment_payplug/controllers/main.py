# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import json

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.logging import get_payment_logger

from .. import const
from ..models.payment_transaction import CANCEL_ROUTE, RETURN_ROUTE, WEBHOOK_ROUTE

_logger = get_payment_logger(__name__, sensitive_keys=const.SENSITIVE_KEYS)


class PayplugController(http.Controller):
    _return_url = RETURN_ROUTE
    _cancel_url = CANCEL_ROUTE
    _webhook_url = WEBHOOK_ROUTE

    @http.route(
        _return_url, type="http", auth="public", methods=["GET"], save_session=False
    )
    def payplug_return(self, reference=None, access_token=None, **_kwargs):
        """Process the return of the customer from the Payplug payment page.

        The route is flagged with `save_session=False` for the same reason as in the
        other redirection-based providers: the session cookie may be missing when coming
        back from an external site, and the redirection to `/payment/status` retrieves
        it.

        :param str reference: The reference of the transaction, embedded in the return
            URL.
        :param str access_token: The access token signing the reference.
        """
        tx_sudo = self._get_transaction(reference, access_token)
        if tx_sudo:
            try:
                tx_sudo._payplug_fetch_and_process()
            except ValidationError:
                _logger.exception(
                    "Unable to fetch the Payplug payment of %s.", reference
                )
        return request.redirect("/payment/status")

    @http.route(
        _cancel_url, type="http", auth="public", methods=["GET"], save_session=False
    )
    def payplug_cancel(self, reference=None, access_token=None, **_kwargs):
        """Process the cancellation of the payment by the customer on Payplug.

        :param str reference: The reference of the transaction, embedded in the cancel
            URL.
        :param str access_token: The access token signing the reference.
        """
        tx_sudo = self._get_transaction(reference, access_token)
        if tx_sudo:
            try:
                tx_sudo._payplug_abort_and_process()
            except ValidationError:
                _logger.exception(
                    "Unable to cancel the Payplug payment of %s.", reference
                )
        return request.redirect("/payment/status")

    @http.route(_webhook_url, type="http", auth="public", methods=["POST"], csrf=False)
    def payplug_webhook(self):
        """Process a notification sent by Payplug.

        The body is not trusted: only the id of the notified object is used, and the
        object is fetched from the API before any update.

        :return: An empty response acknowledging the notification, or an error status
            when the object could not be fetched, so that the notification can be sent
            again.
        """
        try:
            notification_data = json.loads(
                request.httprequest.get_data(as_text=True) or "{}"
            )
        except ValueError:
            _logger.warning("Received a Payplug notification with an invalid body.")
            return request.make_response("", status=400)
        if not isinstance(notification_data, dict):
            return request.make_response("", status=400)
        _logger.info(
            "Notification received from Payplug for %s %s.",
            notification_data.get("object"),
            notification_data.get("id"),
        )
        try:
            request.env["payment.transaction"].sudo()._payplug_handle_notification(
                notification_data
            )
        except ValidationError:
            _logger.exception("Unable to process the Payplug notification.")
            return request.make_response("", status=503)
        return request.make_response("", status=200)

    @staticmethod
    def _get_transaction(reference, access_token):
        """Return the Payplug transaction matching the signed reference, if any.

        :param str reference: The reference of the transaction.
        :param str access_token: The access token signing the reference.
        :return: The transaction, in sudo mode, or an empty recordset.
        :rtype: payment.transaction
        """
        tx_model = request.env["payment.transaction"].sudo()
        if not reference or not payment_utils.check_access_token(
            access_token, reference
        ):
            _logger.warning(
                "Received a Payplug redirection with an invalid access token."
            )
            return tx_model
        return tx_model.search(
            [("reference", "=", reference), ("provider_code", "=", "payplug")], limit=1
        )
