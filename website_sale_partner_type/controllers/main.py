# -*- coding: utf-8 -*-
# © 2016 Nicola Malcontenti - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

website_sale.mandatory_billing_fields = [
    "name", "phone", "email", "street", "city", "country_id"]


class WebsiteSalePartnerType(website_sale):

    def checkout_form_save(self, checkout):
        super(WebsiteSalePartnerType, self).checkout_form_save(
            checkout=checkout)
        partner_id = request.website.sale_get_order(
            context=request.context).partner_id
        if request.params['partner_type'] == 'individual':
            partner_id.write({'is_company': False})
        elif request.params['partner_type'] == 'company':
            partner_id.write({'is_company': True})

    def checkout_form_validate(self, data):
        res = super(WebsiteSalePartnerType, self).checkout_form_validate(
            data=data)
        partner_id = request.website.sale_get_order(
            context=request.context).partner_id
        if request.params['partner_type'] == 'individual':
            partner_id.write({'is_company': False})
        elif request.params['partner_type'] == 'company':
            partner_id.write({'is_company': True})
        if request.params['partner_type'] == 'select':
            res["partner_type"] = 'error'
        return res

    def checkout_values(self, data=None):
        res = super(WebsiteSalePartnerType, self).checkout_values(
            data=data)
        orm_user = request.env['res.users']
        if data:
            if data['partner_type'] == 'individual':
                res['checkout']['partner_type'] = "individual"
            else:
                res['checkout']['partner_type'] = "company"
        else:
            if request.uid == request.website.user_id.id:
                res['checkout']['partner_type'] = 'select'
            else:
                partner = orm_user.sudo().browse([request.uid])[0].partner_id
                if partner.is_company:
                    res['checkout']['partner_type'] = "company"
                else:
                    res['checkout']['partner_type'] = "individual"
        return res
