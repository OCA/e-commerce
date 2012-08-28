# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                      #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
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

from openerp.osv.orm import Model
from openerp.osv import fields
import netsvc

class attribute_shop_location(Model):

    _name = "attribute.shop.location"
    _description = "Attribute Shop Location"
    _order="sequence"

    _inherits = {'product.attribute': 'attribute_id'}

    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'sequence': fields.integer('Sequence'),
        'external_name': fields.char('External Name', size=128, required=True),
    }

