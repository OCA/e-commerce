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


from openerp.osv.orm import Model
from openerp.osv import fields
from base_external_referentials.decorator import only_for_referential
from base_external_referentials.decorator import commit_now

class product_product(Model):
    _inherit='product.product'

    def _check_if_export(self, cr, uid, external_session, product, context=None):
        if context.get('export_product') == 'simple':
            return True
        return False

    @only_for_referential(ref_categ ='Multichannel Sale')
    def _get_last_exported_date(self, cr, uid, external_session, context=None):
        shop = external_session.sync_from_object
        if context.get('export_product') == 'simple':
            return shop.last_products_export_date
        elif context.get('export_product') == 'special':
            return shop.last_special_products_export_date
        return False

    @only_for_referential(ref_categ ='Multichannel Sale')
    @commit_now
    def _set_last_exported_date(self, cr, uid, external_session, date, context=None):
        shop = external_session.sync_from_object
        if context.get('export_product') == 'simple':
            return self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_products_export_date': date}, context=context)
        elif context.get('export_product') == 'special':
            return self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_special_products_export_date': date}, context=context)

    @only_for_referential(ref_categ ='Multichannel Sale')
    def get_ids_and_update_date(self, cr, uid, external_session, ids=None, last_exported_date=None, context=None):
        shop = external_session.sync_from_object
        if shop.exportable_product_ids:
            product_ids = [product.id for product in shop.exportable_product_ids if self._check_if_export(cr, uid, external_session, product, context=context)]
            if ids:
                product_ids = set(ids).intersection(set(product_ids))
            res = super(product_product, self).get_ids_and_update_date(cr, uid, external_session,
                                                            ids=product_ids,
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        else:
            res = (), {} # list of ids, dict of ids to date_changed
        return res

class product_category(Model):
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
        'recursive_children_ids': fields.function(_get_recursive_children_ids, method=True, type='one2many', relation="product.category", string='All Child Categories'),
    }

    @only_for_referential(ref_categ ='Multichannel Sale')
    def _get_last_exported_date(self, cr, uid, external_session, context=None):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'], context=context)
        return shop.last_category_export_date

    @only_for_referential(ref_categ ='Multichannel Sale')
    @commit_now
    def _set_last_exported_date(self, cr, uid, external_session, date, context=None):
        return self.pool.get('sale.shop').write(cr, uid, context['sale_shop_id'], {'last_category_export_date': date}, context=context)

    def get_ids_and_update_date(self, cr, uid, external_session, ids=None, last_exported_date=None, context=None):
        shop = self.pool.get('sale.shop').browse(cr, uid, context['sale_shop_id'],context=context)
        if shop.exportable_category_ids:
            res = super(product_category, self).get_ids_and_update_date(cr, uid, external_session,
                                                            ids=[product.id for product in shop.exportable_category_ids],
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        else:
            res= [False, False]
        return res

