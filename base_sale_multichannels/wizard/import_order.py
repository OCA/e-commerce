# -*- coding: utf-8 -*-
##############################################################################
#
#    Base_sale_multichannels module for OpenERP
#    Copyright (C) 2010 Sébastien BEAU <sebastien.beau@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields,osv
from tools.translate import _
from base_external_referentials.external_osv import ExternalSession

class sale_order_import_wizard(osv.osv_memory):
    _name = 'sale.order.import.wizard'
    _description = 'sale order import wizard'

    _columns = {
        'order_number': fields.char('Order Number', size=64),
        }

    def import_order(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        shop = self.pool.get('sale.shop').browse(cr, uid, context['active_id'], context=context)
        external_session = ExternalSession(shop.referential_id, shop)
        wizard = self.browse(cr, uid, ids[0], context=context)
        self.pool.get('sale.order')._import_one_resource(cr, uid, external_session, wizard.order_number, context=context)
        return {'type': 'ir.actions.act_window_close'}
