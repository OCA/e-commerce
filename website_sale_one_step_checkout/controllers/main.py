# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

from werkzeug.exceptions import Forbidden


class WebsiteSale(WebsiteSale):
    def _get_address_data(self, **kw):
        Partner = request.env['res.partner'] \
            .with_context(show_address=True).sudo()
        order = request.website.sale_get_order(force_create=True)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}
        mode = None
        partner_id = kw.get('partner_id')
        partner_id = int(partner_id) if partner_id else None
        shippings = []

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search(
                    [('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([
                        ('id', 'child_of',
                         order.partner_id.commercial_partner_id.ids)],
                        order='id desc')
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                values = Partner.browse(partner_id)
            elif partner_id is None:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw,
                                                            pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode,
                                                              pre_values,
                                                              errors,
                                                              error_msg)

            if errors:
                errors['error_message'] = error_msg
                return {
                    'success': False,
                    'errors': errors
                }

            partner_id = self._checkout_form_save(mode, post, kw)
            if mode[1] == 'billing':
                order.partner_id = partner_id
                order.onchange_partner_id()

                # If the public user specifies a shipping address
                # those form values fill be prepended with 'shipping_'.
                # Also we reach this part here only after successful form
                # validation, so no further validation is needed here.
                # In case of a delivery address, we need to
                #   1. Filter out the shipping information
                #   2. Create a new partner which will be then linked
                #      to the sale order
                if "delivery_address" in kw:
                    shipping_values = {k.split('shipping_')[1]: kw[k] for k
                                       in kw if k.startswith('shipping_')}
                    # use Odoo's internal function to get post values
                    # discard the errors, since at this step none
                    # will be present
                    shipping_post, _, _ = self.values_postprocess(
                        order, ('new', 'shipping'), shipping_values,
                        errors, error_msg)
                    shipping_partner = self._checkout_form_save(
                        ('new', 'shipping'), shipping_post, None)
                    order.partner_shipping_id = shipping_partner
            elif mode[1] == 'shipping':
                order.partner_shipping_id = partner_id

            order.message_partner_ids = [
                (4, partner_id), (3, request.website.partner_id.id)
            ]
            if not shippings:
                shippings = Partner.search(
                    [('id', 'child_of',
                      order.partner_id.commercial_partner_id.ids)],
                    order='id desc')
            render_values = {
                'shippings': shippings,
                'order': order
            }
            if mode[0] == 'new':
                # New public user address
                # To avoid access problems when rendering
                # the address template, fetch new values
                render_values = self.checkout(**{'public_user': True})

            return {
                'success': True,
                'values': render_values,
                'mode': mode
            }

        country = 'country_id' in values and values['country_id'] != '' and \
                  request.env['res.country'].browse(
                      int(values['country_id']))
        country = country and country.exists() or def_country_id

        return {
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }

    @http.route(['/shop/checkout/render_address'], type='json', auth='public',
                website=True, multilang=True)
    def render_address(self, **kw):
        """Fetch address data and render modal template if necessary.

        Modal template with corresponding address data needs to be rendered
        only for logged in user. In this case, if all the validation steps went
        fine, a dictionary will be returned by `_get_address_data`.

        In all the other cases, e.g. when public user, errors, redirection etc.
        return the result without further processing.
        """
        address_data = self._get_address_data(**kw)

        if not isinstance(address_data, dict) or address_data.get('errors'):
            return address_data

        values = address_data.get('values') or address_data

        if 'submitted' in kw:
            del address_data['values']
            address_data.update(
                {'template': request.env['ir.ui.view'].render_template(
                    "website_sale_one_step_checkout.address", values)})

            return address_data

        template = request.env['ir.ui.view'].render_template(
            "website_sale_one_step_checkout.checkout_new_address_modal",
            values)
        return {
            'success': True,
            'template': template,
            'type': values['mode'][1],
            'modal_title': _(kw.get('modal_title', ''))
        }

    @http.route(['/shop/checkout'], type='http', auth='public',
                website=True, multilang=True)
    def checkout(self, **post):
        """Use one step checkout if enabled. Fall back to normal otherwise."""
        if not request.website.use_osc:
            return super(WebsiteSale, self).checkout(**post)

        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(**post)

        if post.get('public_user'):
            return values

        result = self.payment(post=post)
        values.update(result.qcontext)

        address_data = self._get_address_data(**post)
        values.update(address_data)

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'

        return request.render(
            'website_sale_one_step_checkout.osc_onestepcheckout', values)

    @http.route(['/shop/checkout/validate_checkout_data'], type='json',
                auth='public', website=True, multilang=True)
    def validate_checkout_data(self, **post):
        order = request.website.sale_get_order()
        result = {
            'success': False
        }

        if not order:
            return result

        if order.partner_id.id != request.website.user_id.sudo().partner_id.id:
            for f in self._get_mandatory_billing_fields():
                if not order.partner_id[f]:
                    result['partner_id'] = order.partner_id.id
                    return result
            result['success'] = True

        return result

    @http.route()
    def address(self, **post):
        if not request.website.use_osc:
            return super(WebsiteSale, self).address(**post)

        return request.redirect('/shop')

    @http.route(['/shop/checkout/proceed_payment/'], type='json',
                auth='public', website=True, multilang=True)
    def proceed_payment(self, **post):
        # must have a draft sale order with lines at this point
        #  otherwise redirect to shop
        SaleOrder = request.env['sale.order']
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # part from shop/confirm_order
        order.onchange_partner_shipping_id()
        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        extra_step = request.env.ref('website_sale.extra_info_option')

        if extra_step.active:
            return request.redirect("/shop/extra_info")

        values = {
            'website_sale_order': order
        }
        values['errors'] = SaleOrder._get_errors(order)
        values.update(SaleOrder._get_website_data(order))

        if values['errors']:
            return values
