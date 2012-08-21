# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_links_sync for OpenERP                                            #
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

from openerp.osv.orm import Model
from openerp.osv import fields
import netsvc
from tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime



class sale_shop(Model):
    _inherit = "sale.shop"

    _columns = {
        'last_products_links_export_date' : fields.datetime('Last Product Link Export Time'),
    }

    def export_catalog(self, cr, uid, ids, context=None):
        res=super(sale_shop, self).export_catalog(cr, uid, ids, context=context)
        context['export_product'] = 'link'
        self.export_resources(cr, uid, ids, 'product.product', context=context)
        return res



