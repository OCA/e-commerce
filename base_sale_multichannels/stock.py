# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
#########################################################################
#                                                                       #
# Copyright (C) 2010 BEAU Sébastien                                     #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
from tools.translate import _

class stock_picking(Model):
    _inherit = "stock.picking"

    _columns = {
        'do_not_export': fields.boolean(
            'Do not export',
            help="This delivery order will not be exported to the "
                 "external referential."
        ),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def create_ext_shipping(self, cr, uid, id, picking_type, external_referential_id, context):
        raise except_osv(_("Not Implemented"), _("Not Implemented in abstract base module!"))

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, \
                                                            inv_type, journal_id, context=context)
        vals['shop_id'] = picking.shop_id.id
        return vals
