# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    base_sale_multichannels for OpenERP                                        #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from openerp.osv.orm import Model
from openerp.osv import fields


class res_partner(Model):
    _inherit='res.partner'

    _columns = {
        # defaults_shop_id is deprecated... we should not use it any more !
        'defaults_shop_id': fields.many2one('sale.shop', 'Sale Shop', help="This is the default shop of the customer"),
        'shop_ids': fields.many2many('sale.shop', 'sale_shop_res_partner_rel', 'shop_id', 'partner_id', 'Present in Shops', readonly=True, help="List of shops in which this customer exists."),
    }

    def _get_default_import_values(self, cr, uid, external_session, mapping_id=None, defaults=None, context=None):
        if external_session.sync_from_object._name == 'sale.shop':
            shop = external_session.sync_from_object
            if not defaults: defaults = {}
            defaults.update({
                'lang': shop.default_customer_lang.code,
                'property_account_position': shop.default_fiscal_position.id,
                'property_account_receivable': shop.default_customer_account,
                'shop_ids': [(4, shop.id)],
            })
        return defaults

class res_partner_address(Model):
    _inherit='res.partner.address'

    def _transform_one_resource(self, *args, **kwargs):
        if kwargs.get('parent_data') and kwargs['parent_data'].get('partner_id'):
            kwargs['defaults']['partner_id'] = kwargs['parent_data']['parent_id']
        return super(res_partner_address, self)._transform_one_resource(*args, **kwargs)
