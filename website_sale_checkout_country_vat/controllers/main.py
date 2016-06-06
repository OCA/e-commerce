# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):

    def _get_vat_code(self, code=None):
        if code:
            return request.env['res.country'].search([
                ('code', '=', code)
            ])
        return (request.website.vat_code_id or
                request.website.company_id.country_id)

    @http.route(
        ['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        if 'vat' in post:
            if post['country_vat_code'] != post['vat'][:2]:
                post['vat'] = '%s%s' % (
                    post['country_vat_code'], post['vat'])
        return super(WebsiteSale, self).confirm_order(**post)

    def checkout_values(self, data=None):
        res = super(WebsiteSale, self).checkout_values(data)
        if 'checkout' in res:
            vat = res['checkout'].get('vat', '')
            if 'country_vat_code' not in res['checkout']:
                res['checkout']['country_vat_code'] = vat[:2]
            res['checkout']['vat_code'] = res['checkout'].get(
                'country_vat_code', '')
            res['country_vat_code_id'] = self._get_vat_code(
                res['checkout']['vat_code']).id
        return res

    def checkout_parse(self, address_type, data, remove_prefix=False):
        res = super(WebsiteSale, self).checkout_parse(
            address_type, data, remove_prefix)
        if 'country_vat_code' in data:
            res['country_vat_code'] = data['country_vat_code']
        return res

    def checkout_form_validate(self, data):
        error = super(WebsiteSale, self).checkout_form_validate(data)
        if error.get('vat', '') == 'error':
            if (data['country_vat_code'] == data['vat'][:2]):
                data['vat'] = data['vat'][2:]
        return error
