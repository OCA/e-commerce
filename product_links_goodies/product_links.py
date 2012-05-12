# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_links_goodies for OpenERP                                         #
#   Copyright (C) 2012 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import osv, fields
import netsvc


class product_link(osv.osv):
    _inherit = "product.link"
    
    _columns = {
        'quantity': fields.float('Quantity'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'supplier_goodies': fields.boolean('Supplier Goodies', help=("If it's a supplier goodies "
                                "the product will be automatically added to the purchase order")),
        'cost_price': fields.float('Cost Price'),
    }

    def get_link_type_selection(self, cr, uid, context=None):
        res = super(product_link, self).get_link_type_selection(cr, uid, context=context)
        res.append(('goodies', 'Goodies'))
        return res

