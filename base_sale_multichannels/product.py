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
        res = (), {} # list of ids, dict of ids to date_changed
        shop = external_session.sync_from_object
        if shop.exportable_product_ids:
            product_ids = [product.id for product in shop.exportable_product_ids if self._check_if_export(cr, uid, external_session, product, context=context)]
            if ids:
                product_ids = set(ids).intersection(set(product_ids))
            if product_ids:
                res = super(product_product, self).get_ids_and_update_date(cr, uid, external_session,
                                                            ids=product_ids,
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        return res

    def _get_categories_ids_for_shop(self, cr, uid, product_id, shop_id, context=None):
        shop_obj = self.pool.get('sale.shop')
        shop_values = shop_obj.read(cr, uid, shop_id,
                                    ['exportable_category_ids'],
                                    context=context)
        shop_categ_ids = set(shop_values['exportable_category_ids'])
        product = self.read(cr, uid, product_id, ['categ_ids', 'categ_id'], context=context)
        product_categ_ids = set(product['categ_ids'])
        product_categ_ids.add(product['categ_id'][0])
        return list(product_categ_ids & shop_categ_ids)

    def _get_or_create_ext_category_ids_for_shop(self, cr, uid, external_session, product_id, context=None):
        res = []
        categ_obj = self.pool.get('product.category')
        for oe_categ_id in self._get_categories_ids_for_shop(cr, uid, product_id, external_session.sync_from_object.id, context=context):
            res.append(categ_obj.get_or_create_extid(cr, uid, external_session, oe_categ_id, context=context))
        return res

class product_template(Model):
    _inherit = 'product.template'

    #TODO implement set function and also support multi tax
    def _get_tax_group_id(self, cr, uid, ids, field_name, args, context=None):
        result = {}
        for product in self.browse(cr, uid, ids, context=context):
            result[product.id] = product.taxes_id and product.taxes_id[0].group_id.id
        return result

    _columns = {
        'tax_group_id': fields.function(_get_tax_group_id,
                            string='Tax Group',
                            type='many2one',
                            relation='account.tax.group',
                            store=False,
                            help=('Tax group are use with some external',
                                  ' system like magento or prestashop')),
    }


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
        shop = external_session.sync_from_object
        return shop.last_category_export_date

    @only_for_referential(ref_categ ='Multichannel Sale')
    @commit_now
    def _set_last_exported_date(self, cr, uid, external_session, date, context=None):
        shop = external_session.sync_from_object
        return self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_category_export_date': date}, context=context)

    def get_ids_and_update_date(self, cr, uid, external_session, ids=None, last_exported_date=None, context=None):
        shop = external_session.sync_from_object
        if shop.exportable_category_ids:
            res = super(product_category, self).get_ids_and_update_date(cr, uid, external_session,
                                                            ids=[categ.id for categ in shop.exportable_category_ids],
                                                            last_exported_date=last_exported_date,
                                                            context=context)
        else:
            res = (), {} # list of ids, dict of ids to date_changed
        return res

