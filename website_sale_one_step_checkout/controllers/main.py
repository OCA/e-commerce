# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

from werkzeug.exceptions import Forbidden


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth='public',
                website=True, multilang=True)
    def checkout(self, **post):
        """Use one step checkout if enabled. Fall back to normal otherwise."""
        # if onestepcheckout is deactivated use the normal checkout
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

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'

        return request.render(
            'website_sale_one_step_checkout.osc_onestepcheckout', values)

    @http.route(['/shop/checkout/validate_address_form'], type='json',
                auth='public', website=True, multilang=True)
    def validate_address_form(self):
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

        elif order.partner_id.id == request.website.user_id\
                .sudo().partner_id.id:
            return result

    @http.route()
    def address(self, **post):
        if not request.website.use_osc:
            return super(WebsiteSale, self).address(**post)
        else:
            return request.redirect('/shop')

    @http.route(['/shop/checkout/render_address'], type='json', auth='public',
                website=True, multilang=True)
    def render_address(self, **kw):
        Partner = request.env['res.partner']\
            .with_context(show_address=1).sudo()
        order = request.website.sale_get_order(force_create=1)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        mode = (False, False)
        partner_id = int(kw.get('partner_id', -1))
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
            if partner_id > 0:
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
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
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
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
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

                template = request.env['ir.ui.view'].render_template(
                    "website_sale_one_step_checkout.address", render_values)
                return {
                    'success': True,
                    'template': template,
                    'mode': mode
                }

        country = 'country_id' in values and values['country_id'] != '' and \
                  request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }

        template = request.env['ir.ui.view'].render_template(
            "website_sale_one_step_checkout.checkout_new_address_modal",
            render_values)
        return {
            'success': True,
            'template': template,
            'type': mode[1],
            'modal_title': _(kw.get('modal_title', ''))
        }

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
            raise NotImplementedError('Action must be defined!')
