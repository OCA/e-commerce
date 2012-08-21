# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    amazonerpconnect for OpenERP                                               #
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

from osv import osv, fields

class res_partner(osv.osv):
    _inherit='res.partner'
    
    _columns = {
        'defaults_shop_id': fields.many2one('sale.shop', 'Sale Shop', help="This is the default shop of the customer"),
    }
    
    def _get_default_import_values(self, cr, uid, external_session, mapping_id=None, defaults=None, context=None):
        shop_id = context.get('sale_shop_id')
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
            if not defaults: defaults = {}
            defaults.update({
                    'lang': shop.default_customer_lang.id
            })
        return defaults

res_partner()

class res_partner_address(osv.osv):
    _inherit='res.partner.address'
    
    def _transform_one_resource(self, *args, **kwargs):
        if kwargs.get('parent_data') and kwargs['parent_data'].get('partner_id'):
            kwargs['defaults']['partner_id'] = kwargs['parent_data']['parent_id']
        return super(res_partner_address, self)._transform_one_resource(*args, **kwargs)
