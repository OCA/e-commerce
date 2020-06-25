import logging

from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment_slimpay.controllers.main import SlimpayController


_logger = logging.getLogger(__name__)


class SlimpayControllerWebsiteSale(SlimpayController, WebsiteSale):

    @http.route(['/payment/slimpay_transaction/<int:acquirer_id>'],
                type='json', auth="public", website=True)
    def payment_slimpay_transaction(
            self, acquirer_id, tx_type='form', token=None, **kwargs):
        """ Slimpay specific payment transaction creation. Uses the standard
        website_sale method, but creates the slimpay order and respond with
        slimpay's redirect URL instead of a form to be submitted.
        """
        # When a previous error occured, the tx id may stay in the
        # session and generate an error here after
        if 'sale_transaction_id' in request.session:
            del request.session['sale_transaction_id']
        self.payment_transaction(
            acquirer_id, tx_type='form', token=token, **kwargs)
        so = request.env['sale.order'].sudo().browse(
            request.session['sale_order_id'])
        validated_payment_url = '/shop/payment/validate'
        if token:
            self._pay_with_token(so.payment_tx_id)
            return validated_payment_url
        else:
            return self._approval_url(so, acquirer_id, validated_payment_url)

    def _pay_with_token(self, tx):
        """Use Slimpay s2s API to create a payment with transaction's token,
        then confirm the sale as usual.
        """
        if tx.slimpay_s2s_do_transaction():
            tx._confirm_so(acquirer_name='slimpay')
        else:
            raise UserError(
                _('Transaction error: take a screenshot and contact us'))

    def _get_mandatory_billing_fields(self):
        ''' Replace "name" by "firstname" and "lastname" '''
        fields = super(SlimpayController, self)._get_mandatory_billing_fields()
        return ['firstname', 'lastname'] + [f for f in fields if f != 'name']

    def _get_mandatory_shipping_fields(self):
        ''' Replace "name" by "firstname" and "lastname" '''
        fields = super(SlimpayController,
                       self)._get_mandatory_shipping_fields()
        return ['firstname', 'lastname'] + [f for f in fields if f != 'name']

    def values_postprocess(self, order, mode, values, errors, error_msg):
        """ Do not drop firstname and lastname fields for `partner_firstname`
        module compatiblity. """
        new_values, errors, error_msg = super(
            SlimpayController, self).values_postprocess(order, mode, values,
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
            SlimpayController, self).checkout_form_validate(
                mode, all_form_values, data)
        order = request.website.sale_get_order()
        partner = order.partner_id
        for field, msg in partner.slimpay_checks(all_form_values).items():
            errors[field] = 'error'
            error_msg.append(msg)
        return errors, error_msg
