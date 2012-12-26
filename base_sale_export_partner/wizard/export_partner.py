# -*- coding: utf-8 -*-
##############################################################################
#
#    Base sale export partner module for OpenERP
#    Copyright (C) 2012 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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


from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from base_external_referentials.external_osv import ExternalSession

class partner_export_wizard(TransientModel):
    _name = 'partner.export.wizard'
    _description = 'partner export wizard'


    _columns = {
        'shop': fields.many2many('sale.shop', 'shop_partner_rel', 'shop_id', 'partner_id', 'Shop', required=True),
        }


    def export_partner(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        shop_ids = self.read(cr, uid, id, context=context)[0]['shop']
        sale_shop_obj = self.pool.get('sale.shop')
        partner_obj = self.pool.get('res.partner')
        addr_obj = self.pool.get('res.partner.address')
        partner_ids = context.get('active_ids')
        if not partner_ids:
            # This should never happen
            raise osv.except_osv(_('User Error'), 'No partner selected!')

        for shop in sale_shop_obj.browse(cr, uid, shop_ids, context=context):
            if not shop.referential_id:
                raise except_osv(_("User Error"), _("The shop '%s' doesn't have any external referential. Are you sure that it's an external sale shop? If yes, synchronize it before exporting partners." % shop.name))
            external_session = ExternalSession(shop.referential_id, shop)
            context = self.pool.get('sale.shop').init_context_before_exporting_resource(cr, uid, external_session, shop.id, 'res.partner', context=context)
            for partner in partner_obj.read(cr, uid, partner_ids, ['address'], context=context):
                partner_obj._export_one_resource(cr, uid, external_session, partner['id'], context=context)
                partner_obj.write(cr, uid, partner['id'], {
                    'shop_ids': [(4, shop.id)],
                    }, context=context)
                for address_id in partner['address']:
                    addr_obj._export_one_resource(cr, uid, external_session, address_id, context=context)
        return {'type': 'ir.actions.act_window_close'}

