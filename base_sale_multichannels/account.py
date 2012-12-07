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

class account_tax_code(Model):
    _inherit='account.tax'
    
    def get_tax_from_rate(self, cr, uid, rate, is_tax_included=False, context=None):
        #TODO improve, if tax are not correctly mapped the order should be in exception (integration with sale_execption)
        tax_ids = self.pool.get('account.tax').search(cr, uid, [('price_include', '=', is_tax_included),
                ('type_tax_use', 'in', ['sale', 'all']), ('amount', '>=', rate - 0.001), ('amount', '<=', rate + 0.001)])
        if tax_ids and len(tax_ids) > 0:
            return tax_ids[0]
        else:
        #try to find a tax with less precision 
            tax_ids = self.pool.get('account.tax').search(cr, uid, [('price_include', '=', is_tax_included), 
                    ('type_tax_use', 'in', ['sale', 'all']), ('amount', '>=', rate - 0.01), ('amount', '<=', rate + 0.01)])
            if tax_ids and len(tax_ids) > 0:
                return tax_ids[0]
        return False

class account_tax_group(Model):
    _name = 'account.tax.group'
    _description = 'account tax group'

    _columns = {
        'name': fields.char('Name', size=64),
        'tax_ids': fields.one2many('account.tax', 'group_id', 'Taxes'),
    }

class account_tax(Model):
    _inherit = 'account.tax'

    _columns = {
        'group_id': fields.many2one('account.tax.group', 'Tax Group', help=("Choose the tax group."
                                   " This is needed for example with magento or prestashop")),
    }


