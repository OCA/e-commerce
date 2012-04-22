    # -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_sale_multichannels for OpenERP                                       #
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
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
from base_external_referentials.decorator import only_for_referential

class product_product(osv.osv):
    _inherit='product.product'

    @only_for_referential(ref_categ ='Multichannel Sale')#, module_name=__name__)
    def _get_last_exported_date(self, cr, uid, external_session, context):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'], context=context)
        return shop.last_products_export_date

    @only_for_referential(ref_categ ='Multichannel Sale')#, module_name=__name__)
    def _set_last_exported_date(self, cr, uid, external_session, date, context):
        return self.pool.get('sale.shop').write(cr, uid, context['sale_shop_id'], {'last_products_export_date': date}, context=context)

    def get_ids_and_update_date(self, cr, uid, ids=None, last_exported_date=None, context=None):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'],context=context)
        if shop.exportable_product_ids:
            res = super(product_product, self).get_ids_and_update_date(cr, uid, 
                                                            ids=[product.id for product in shop.exportable_product_ids],
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        else:
            res= []
        return res

class product_category(osv.osv):
    _inherit = "product.category"
    
    def collect_children(self, category, children=None):
        if children is None:
            children = []

        for child in category.child_id:
            children.append(child.id)
            self.collect_children(child, children)

        return children
    
    def _get_recursive_children_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for category in self.browse(cr, uid, ids):
            res[category.id] = self.collect_children(category, [category.id])
        return res

    _columns = {
        'recursive_childen_ids': fields.function(_get_recursive_children_ids, method=True, type='one2many', relation="product.category", string='All Child Categories'),
    }

    @only_for_referential(ref_categ ='Multichannel Sale')#, module_name=__name__)
    def _get_last_exported_date(self, cr, uid, external_session, context):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'], context=context)
        return shop.last_category_export_date

    @only_for_referential(ref_categ ='Multichannel Sale')#, module_name=__name__)
    def _set_last_exported_date(self, cr, uid, external_session, date, context):
        return self.pool.get('sale.shop').write(cr, uid, context['sale_shop_id'], {'last_category_export_date': date}, context=context)

    def get_ids_and_update_date(self, cr, uid, ids=None, last_exported_date=None, context=None):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'],context=context)
        if shop.exportable_category_ids:
            res = super(product_category, self).get_ids_and_update_date(cr, uid, 
                                                            ids=[product.id for product in shop.exportable_category_ids],
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        else:
            res= []
        return res

