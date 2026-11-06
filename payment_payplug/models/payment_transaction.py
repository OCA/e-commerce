# Copyright 2026 Sébastien Berger (sbinfo67)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import SQL, urls

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.logging import get_payment_logger

from .. import const

_logger = get_payment_logger(__name__, sensitive_keys=const.SENSITIVE_KEYS)

RETURN_ROUTE = "/payment/payplug/return"
CANCEL_ROUTE = "/payment/payplug/cancel"
WEBHOOK_ROUTE = "/payment/payplug/webhook"

PHONE_CLEANUP_RE = re.compile(r"[\s.\-()/]")
E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")
FRENCH_MOBILE_RE = re.compile(r"^\+33[67]\d{8}$")


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    # === BUSINESS METHODS - PAYMENT FLOW === #

    def _get_specific_rendering_values(self, processing_values):
        """Override of `payment` to create the payment and return the form values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the
                                       transaction.
        :return: The dict of provider-specific rendering values.
        :rtype: dict
        """
        if self.provider_code != "payplug":
            return super()._get_specific_rendering_values(processing_values)

        amount_error = self._payplug_check_amount_limits()
        if amount_error:
            self._set_error(amount_error)
            return {}

        payload = self._payplug_prepare_payment_payload()
        try:
            payment_data = self._send_api_request("POST", "payments", json=payload)
        except ValidationError as error:
            self._set_error(str(error))
            return {}

        # Store the Payplug id now to fetch the payment after the redirection and to
        # match the notifications.
        self.provider_reference = payment_data.get("id")
        payment_url = (payment_data.get("hosted_payment") or {}).get("payment_url")
        if not payment_url:
            self._set_error(self.env._("Payplug did not return any payment page URL."))
            return {}

        # Pass the query parameters separately: a GET form drops the query string of its
        # action.
        split_url = urlsplit(payment_url)
        url_params = dict(parse_qsl(split_url.query))
        api_url = urlunsplit(split_url._replace(query=""))
        return {"api_url": api_url, "url_params": url_params}

    def _payplug_check_amount_limits(self):
        """Return an error message if the amount is outside the Payplug card limits.

        :return: The error message, if any.
        :rtype: str|None
        """
        if self.payment_method_id.code in const.PAYMENT_METHODS_MAPPING:
            # The limits of alternative payment methods differ; let Payplug decide.
            return None
        amount = payment_utils.to_minor_currency_units(self.amount, self.currency_id)
        if (
            amount < const.MINIMUM_PAYMENT_AMOUNT
            or amount > const.MAXIMUM_PAYMENT_AMOUNT
        ):
            return self.env._(
                "Payplug only accepts card payments between %(minimum)s and "
                "%(maximum)s.",
                minimum=self.currency_id.format(
                    payment_utils.to_major_currency_units(
                        const.MINIMUM_PAYMENT_AMOUNT, self.currency_id
                    )
                ),
                maximum=self.currency_id.format(
                    payment_utils.to_major_currency_units(
                        const.MAXIMUM_PAYMENT_AMOUNT, self.currency_id
                    )
                ),
            )
        return None

    def _payplug_prepare_payment_payload(self):
        """Create the payload of the payment creation request.

        See https://docs.payplug.com/api/apiref.html#create-a-payment

        :return: The request payload.
        :rtype: dict
        """
        self.ensure_one()
        base_url = self.provider_id.get_base_url()
        url_params = urlencode(
            {
                "reference": self.reference,
                "access_token": payment_utils.generate_access_token(
                    self.reference, env=self.env
                ),
            }
        )
        billing = self._payplug_prepare_customer_values()
        shipping = dict(billing, delivery_type="BILLING")
        payload = {
            "amount": payment_utils.to_minor_currency_units(
                self.amount, self.currency_id
            ),
            "currency": self.currency_id.name,
            "billing": billing,
            "shipping": shipping,
            "hosted_payment": {
                "return_url": f"{urls.urljoin(base_url, RETURN_ROUTE)}?{url_params}",
                "cancel_url": f"{urls.urljoin(base_url, CANCEL_ROUTE)}?{url_params}",
            },
            "notification_url": urls.urljoin(base_url, WEBHOOK_ROUTE),
            "description": self.reference[: const.DESCRIPTION_MAX_LENGTH],
            "metadata": {"odoo_reference": self.reference},
        }
        payplug_method = const.PAYMENT_METHODS_MAPPING.get(self.payment_method_id.code)
        if payplug_method:
            payload["payment_method"] = payplug_method
        return payload

    def _payplug_prepare_customer_values(self):
        """Return the billing values of the customer, without the empty ones.

        :return: The billing values.
        :rtype: dict
        """
        first_name, last_name = payment_utils.split_partner_name(
            self.partner_name or ""
        )
        lang = (self.partner_lang or "").split("_")[0]
        values = {
            "first_name": first_name or last_name,
            "last_name": last_name or first_name,
            "email": self.partner_email,
            "address1": self.partner_id.street or self.partner_address,
            "address2": self.partner_id.street2,
            "postcode": self.partner_zip,
            "city": self.partner_city,
            "country": self.partner_country_id.code,
            "company_name": self.partner_id.commercial_company_name,
            "language": lang
            if lang in const.SUPPORTED_LANGUAGES
            else const.DEFAULT_LANGUAGE,
        }
        phone = self._payplug_format_phone(self.partner_phone)
        if phone:
            key = (
                "mobile_phone_number"
                if FRENCH_MOBILE_RE.match(phone)
                else "landline_phone_number"
            )
            values[key] = phone
        cleaned_values = {}
        for key, value in values.items():
            if not value:
                continue
            max_length = const.FIELD_MAX_LENGTHS.get(key)
            cleaned_values[key] = value[:max_length] if max_length else value
        return cleaned_values

    @api.model
    def _payplug_format_phone(self, phone):
        """Return the phone number in the E.164 format expected by Payplug, or None.

        Only numbers already in international format (with `+` or `00`) are kept:
        guessing the country of a local number could send a wrong number.
        """
        if not phone:
            return None
        phone = PHONE_CLEANUP_RE.sub("", phone)
        if phone.startswith("00"):
            phone = "+" + phone[2:]
        return phone if E164_RE.match(phone) else None

    def _payplug_fetch_and_process(self):
        """Fetch the payment from the Payplug API and process it.

        The payment data received from the customer's browser or from a notification are
        never trusted: the payment is always read back from the API with the secret key.

        Note: self.ensure_one()

        :return: None
        :raise ValidationError: If the API request fails.
        """
        self.ensure_one()
        if self.operation == "refund":
            refund_data = self.source_transaction_id._payplug_get_refund(
                self.provider_reference
            )
            self._process("payplug", refund_data)
            return
        if not self.provider_reference:
            _logger.warning(
                "Transaction %s has no Payplug payment id; nothing to fetch.",
                self.reference,
            )
            return
        payment_data = self._send_api_request(
            "GET", f"payments/{self.provider_reference}"
        )
        self._process("payplug", payment_data)

    def _payplug_abort_and_process(self):
        """Abort the unpaid payment after the customer canceled it, then process it.

        Note: self.ensure_one()

        :return: None
        """
        self.ensure_one()
        if not self.provider_reference or self.state not in ("draft", "pending"):
            return
        try:
            payment_data = self._send_api_request(
                "PATCH", f"payments/{self.provider_reference}", json={"aborted": True}
            )
        except ValidationError:
            # The payment may have been paid or failed meanwhile: its status decides.
            _logger.info(
                "Could not abort Payplug payment of transaction %s.", self.reference
            )
            self._payplug_fetch_and_process()
        else:
            self._process("payplug", payment_data)

    # === BUSINESS METHODS - REFUNDS === #

    def _send_refund_request(self):
        """Override of `payment` to send a refund request to Payplug.

        Note: self.ensure_one() from `_refund`
        """
        if self.provider_code != "payplug":
            return super()._send_refund_request()

        amount = payment_utils.to_minor_currency_units(-self.amount, self.currency_id)
        if amount < const.MINIMUM_REFUND_AMOUNT:
            raise ValidationError(
                self.env._(
                    "Payplug does not accept refunds below %s.",
                    self.currency_id.format(
                        payment_utils.to_major_currency_units(
                            const.MINIMUM_REFUND_AMOUNT, self.currency_id
                        )
                    ),
                )
            )
        refund_data = self._send_api_request(
            "POST",
            f"payments/{self.source_transaction_id.provider_reference}/refunds",
            json={"amount": amount, "metadata": {"odoo_reference": self.reference}},
        )
        self._process("payplug", refund_data)

    def _payplug_get_refund(self, refund_id):
        """Fetch a refund of the payment of this transaction from the Payplug API.

        Note: self.ensure_one()

        :param str refund_id: The Payplug id of the refund.
        :return: The refund data.
        :rtype: dict
        """
        self.ensure_one()
        return self._send_api_request(
            "GET", f"payments/{self.provider_reference}/refunds/{refund_id}"
        )

    def _payplug_lock(self):
        """Lock the transaction rows to serialize the processing of notifications."""
        self.env.cr.execute(
            SQL(
                "SELECT id FROM payment_transaction WHERE id IN %s FOR UPDATE",
                tuple(self.ids),
            )
        )

    # === BUSINESS METHODS - NOTIFICATIONS === #

    @api.model
    def _payplug_handle_notification(self, notification_data):
        """Handle a notification sent by Payplug.

        Only the id and the type of the notified object are read from the notification;
        the object itself is then fetched from the API. A forged notification can thus
        only trigger the re-reading of a genuine object, and a replayed one is processed
        idempotently.

        :param dict notification_data: The notification body.
        :return: None
        :raise ValidationError: If an API request fails.
        """
        object_type = notification_data.get("object")
        object_id = notification_data.get("id")
        if not isinstance(object_id, str) or not object_id:
            _logger.warning("Received a Payplug notification without object id.")
            return

        if object_type == "payment":
            tx = self.search(
                [
                    ("provider_code", "=", "payplug"),
                    ("provider_reference", "=", object_id),
                    ("operation", "!=", "refund"),
                ],
                limit=1,
            )
            if not tx:
                _logger.warning(
                    "No Payplug transaction found for payment %s.", object_id
                )
                return
            tx._payplug_lock()
            tx._payplug_fetch_and_process()
        elif object_type == "refund":
            self._payplug_handle_refund_notification(object_id, notification_data)
        else:
            _logger.info("Ignored Payplug notification of type %s.", object_type)

    @api.model
    def _payplug_handle_refund_notification(self, refund_id, notification_data):
        """Process a refund notification.

        The refund transaction is created when the refund was made outside of Odoo (e.g.
        from the Payplug portal).

        :param str refund_id: The Payplug id of the refund.
        :param dict notification_data: The notification body.
        :return: None
        """
        refund_tx = self.search(
            [
                ("provider_code", "=", "payplug"),
                ("provider_reference", "=", refund_id),
                ("operation", "=", "refund"),
            ],
            limit=1,
        )
        if refund_tx:
            refund_tx._payplug_lock()
            refund_tx._payplug_fetch_and_process()
            return

        payment_id = notification_data.get("payment_id")
        source_tx = (
            payment_id
            and isinstance(payment_id, str)
            and self.search(
                [
                    ("provider_code", "=", "payplug"),
                    ("provider_reference", "=", payment_id),
                    ("operation", "!=", "refund"),
                ],
                limit=1,
            )
        )
        if not source_tx:
            _logger.warning("No Payplug transaction found for refund %s.", refund_id)
            return

        # Serialize with the other notifications of the payment to avoid duplicates.
        source_tx._payplug_lock()
        refund_data = source_tx._payplug_get_refund(refund_id)
        if (
            refund_data.get("id") != refund_id
            or refund_data.get("payment_id") != source_tx.provider_reference
        ):
            _logger.warning("Payplug refund %s does not match its payment.", refund_id)
            return

        refund_tx = source_tx.child_transaction_ids.filtered(
            lambda t: t.operation == "refund" and t.provider_reference == refund_id
        )
        odoo_reference = (refund_data.get("metadata") or {}).get("odoo_reference")
        if not refund_tx and odoo_reference:
            refund_tx = source_tx.child_transaction_ids.filtered(
                lambda t: t.operation == "refund" and t.reference == odoo_reference
            )
            if not refund_tx:
                # The refund was requested from Odoo and its transaction is not
                # committed yet; the request that created it processes the response.
                _logger.info(
                    "Refund %s of transaction %s is being processed by Odoo.",
                    odoo_reference,
                    source_tx.reference,
                )
                return
        if not refund_tx:
            if source_tx.state != "done":
                _logger.warning(
                    "Ignored refund %s of unconfirmed transaction %s.",
                    refund_id,
                    source_tx.reference,
                )
                return
            amount = payment_utils.to_major_currency_units(
                refund_data.get("amount") or 0, source_tx.currency_id
            )
            refund_tx = source_tx._create_child_transaction(amount, is_refund=True)
            refund_tx._log_sent_message()
        refund_tx[:1]._process("payplug", refund_data)

    # === BUSINESS METHODS - PROCESSING === #

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """Override of `payment` to extract the reference from the payment data."""
        if provider_code != "payplug":
            return super()._extract_reference(provider_code, payment_data)
        return (payment_data.get("metadata") or {}).get("odoo_reference")

    def _extract_amount_data(self, payment_data):
        """Override of `payment` to extract the amount and currency of the data."""
        if self.provider_code != "payplug":
            return super()._extract_amount_data(payment_data)
        amount = payment_data.get("amount")
        return {
            "amount": payment_utils.to_major_currency_units(amount, self.currency_id)
            if isinstance(amount, int)
            else None,
            "currency_code": payment_data.get("currency"),
        }

    def _apply_updates(self, payment_data):
        """Override of `payment` to update the transaction based on the payment data."""
        if self.provider_code != "payplug":
            return super()._apply_updates(payment_data)

        if self.operation == "refund":
            self._payplug_apply_refund_updates(payment_data)
            return

        error = self._payplug_check_payment_consistency(payment_data)
        if error:
            _logger.warning(
                "Inconsistent Payplug data for %s: %s", self.reference, error
            )
            self._set_error(error)
            return

        self._payplug_update_payment_method(payment_data)

        failure = payment_data.get("failure")
        if payment_data.get("is_paid"):
            self._set_done()
        elif failure:
            code = failure.get("code") or ""
            message = failure.get("message") or code
            if code in const.CANCEL_FAILURE_CODES:
                self._set_canceled(
                    state_message=self.env._(
                        "The payment was canceled on Payplug (%s).", code
                    )
                )
            else:
                self._set_error(
                    self.env._(
                        "The payment was refused by Payplug (%(code)s): %(message)s",
                        code=code,
                        message=message,
                    )
                )
        else:
            self._set_pending()

    def _payplug_check_payment_consistency(self, payment_data):
        """Check that the payment data belong to this transaction.

        :param dict payment_data: The payment data fetched from the API.
        :return: The error message, if any.
        :rtype: str|None
        """
        if payment_data.get("object") != "payment":
            return self.env._("Payplug returned an object that is not a payment.")
        if (
            self.provider_reference
            and payment_data.get("id") != self.provider_reference
        ):
            return self.env._("The Payplug payment id does not match the transaction.")
        if self._extract_reference("payplug", payment_data) != self.reference:
            return self.env._(
                "The Payplug payment does not reference this transaction."
            )
        if bool(payment_data.get("is_live")) != self.is_live:
            return self.env._(
                "The Payplug payment environment (test or live) does not match the "
                "provider."
            )
        return None

    def _payplug_update_payment_method(self, payment_data):
        """Update the payment method with the card brand used, when known."""
        brand = ((payment_data.get("card") or {}).get("brand") or "").lower()
        code = const.CARD_BRANDS_MAPPING.get(brand)
        if not code:
            return
        payment_method = self.env["payment.method"]._get_from_code(code)
        if payment_method and self.payment_method_id.code == "card":
            self.payment_method_id = payment_method

    def _payplug_apply_refund_updates(self, refund_data):
        """Update the refund transaction with the refund data fetched from the API."""
        source_tx = self.source_transaction_id
        if (
            refund_data.get("object") != "refund"
            or refund_data.get("payment_id") != source_tx.provider_reference
            or (
                self.provider_reference
                and refund_data.get("id") != self.provider_reference
            )
        ):
            self._set_error(
                self.env._("The Payplug refund does not match the transaction.")
            )
            return
        if bool(refund_data.get("is_live")) != self.is_live:
            self._set_error(
                self.env._(
                    "The Payplug refund environment (test or live) does not match the "
                    "provider."
                )
            )
            return
        self.provider_reference = refund_data.get("id")
        # A refund exists on Payplug only once accepted: refunds have no status.
        if self._set_done():
            # Post-process the refund now: no customer will browse its status page.
            self.env.ref("payment.cron_post_process_payment_tx")._trigger()

    # === ACTION METHODS === #

    def action_payplug_refresh_status(self):
        """Fetch the status of the transactions from Payplug and update them.

        :return: A client notification.
        :rtype: dict
        """
        payment_utils.check_rights_on_recordset(self)
        for tx in self.sudo().filtered(lambda t: t.provider_code == "payplug"):
            try:
                tx._payplug_fetch_and_process()
            except ValidationError as error:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {"type": "danger", "message": str(error)},
                }
        return {
            "type": "ir.actions.client",
            "tag": "soft_reload",
        }
