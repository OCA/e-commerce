import logging

from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo.addons.account_payment_slimpay.models import slimpay_utils


_logger = logging.getLogger(__name__)


class SlimpayControllerWebsiteSale(WebsiteSale):

    @http.route(['/payment/slimpay_transaction/<int:acquirer_id>'],
                type='json', auth="public", website=True)
    def payment_slimpay_transaction(self, acquirer_id, tx_ref=None):
        """Handle Slimpay specific transaction online payment.

        This controller is called after the standard website_sale
        method that creates the transaction. It fetches this
        transaction to generate a Slimpay payment URL and return it.
        """
        env = request.env

        if request.website.domain:
            _url = 'https://' + request.website.domain
        else:
            _url = env['ir.config_parameter'].sudo().get_param('web.base.url')

        validate_payment_url = _url + '/shop/payment/validate'

        tx = env['payment.transaction'].search([("reference", "=", tx_ref)])
        so = tx.sudo().sale_order_ids[0]
        assert env.user.partner_id.commercial_partner_id == so.partner_id.commercial_partner_id

        return self._approval_url(so, tx, acquirer_id, validate_payment_url)

    def _approval_url(self, so, transaction, acquirer_id, return_url):
        """ Helper to be used with website_sale to get a Slimpay URL for the
        end-user to sign a mandate and create a first payment online."
        """
        acquirer = request.env['payment.acquirer'].sudo().browse(acquirer_id)
        locale = (so.partner_id.lang or 'en_US').split('_')[0]
        # May emit a direct debit only if a mandate exists; unsupported for now
        subscriber = slimpay_utils.subscriber_from_partner(so.partner_id)
        return acquirer.slimpay_client.approval_url(
            transaction.reference, so.id, locale, so.amount_total,
            so.currency_id.name, so.currency_id.decimal_places,
            subscriber, return_url)

    def _get_mandatory_billing_fields(self):
        ''' Replace "name" by "firstname" and "lastname" '''
        fields = super(SlimpayControllerWebsiteSale,
                       self)._get_mandatory_billing_fields()
        return ['firstname', 'lastname'] + [f for f in fields if f != 'name']

    def _get_mandatory_shipping_fields(self):
        ''' Replace "name" by "firstname" and "lastname" '''
        fields = super(SlimpayControllerWebsiteSale,
                       self)._get_mandatory_shipping_fields()
        return ['firstname', 'lastname'] + [f for f in fields if f != 'name']

    def values_postprocess(self, order, mode, values, errors, error_msg):
        """ Do not drop firstname and lastname fields for `partner_firstname`
        module compatiblity. """
        new_values, errors, error_msg = super(
            SlimpayControllerWebsiteSale,
            self).values_postprocess(order, mode, values,
                                     errors, error_msg)
        for field in ('firstname', 'lastname'):
            if field in values:
                _logger.debug(
                    "payment_slimpay postprocess: %s value has finally *not* "
                    "been dropped.", field)
                new_values[field] = values[field]
        return new_values, errors, error_msg

    def checkout_form_validate(self, mode, all_form_values, data):
        """ Validate partner constraints wrt Slimpay's rule """
        errors, error_msg = super(
            SlimpayControllerWebsiteSale, self).checkout_form_validate(
                mode, all_form_values, data)
        order = request.website.sale_get_order()
        partner = order.partner_id
        for field, msg in partner.slimpay_checks(all_form_values).items():
            errors[field] = 'error'
            error_msg.append(msg)
        return errors, error_msg
