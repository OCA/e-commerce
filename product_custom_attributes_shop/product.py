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
from openerp.osv.osv import except_osv
import netsvc
from lxml import etree
from openerp.tools.translate import _
import re


class product_product(Model):
    _inherit = "product.product"

    def _build_shop_attributes_notebook(self, cr, uid, shops, context=None):
        notebook = etree.Element('notebook', name="shop_attributes_notebook", colspan="4")
        toupdate_fields = []
        for shop in shops:
            page = etree.SubElement(notebook, 'page', string=shop.name.capitalize())
            for attribute in shop.shop_attribute_ids:
                toupdate_fields.append(attribute.name)
                self._build_attribute_field(cr, uid, page, attribute, context=context)
        return notebook, toupdate_fields

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            eview = etree.fromstring(result['arch'])
            info_page = eview.xpath("//page[@string='Information']")
            if info_page:
                info_page = info_page[0]
                shop_obj = self.pool.get('sale.shop')
                shop_ids = shop_obj.search(cr, uid, [], context=context)
                shops = []
                for shop in shop_obj.browse(cr, uid, shop_ids, context=context):
                    if shop.shop_attribute_ids:
                        shops.append(shop)
                if shops:
                    attributes_notebook, toupdate_fields = self._build_shop_attributes_notebook(cr, uid, shops, context=context)
                    result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))
                    main_page = etree.Element('page', string=_('Shop Attributes'))
                    main_page.append(attributes_notebook)
                    info_page.addnext(main_page)
                    result['arch'] = etree.tostring(eview, pretty_print=True)
                    result = self._fix_size_bug(cr, uid, result, context=context)
        return result

    def check_if_activable(self, cr, uid, vals, context=None):
        categ_ids = [vals['categ_id']] + vals.get('categ_ids', [])
        for key in vals.keys():
            if re.match('x_shop.*?_attr_active', key) and vals[key]:
                shop_id = int(key.replace('x_shop', '').replace('_attr_active', ''))
                if not self.pool.get('product.category').check_if_in_shop_category(cr, uid, categ_ids, shop_id, context=context):
                    shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
                    raise except_osv(
                        _("User Error"), 
                        _("The product must be in an children of one of this categories \"%s\" "
                             "in order to be activable on the shop \"%s\"")
                        %('", "'.join([categ.name for categ in shop.exportable_root_category_ids]), shop.name))

    def create(self, cr, uid, vals, context=None):
        if context is None: context={}
        if not context.get('do_not_check_active_field_on_shop'):
            vals['categ_ids'] = vals.get('categ_ids', [(6,0,[])])[0][2]
            self.check_if_activable(cr, uid, vals, context=context)
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context={}
        need_check = False
        if not context.get('do_not_check_active_field_on_shop'):
            for key in vals.keys():
                if re.match('x_shop.*?_attr_active', key) and vals[key] or key in ('categ_id', 'categ_ids'):
                    need_check = True
                    break
        res = super(product_product, self).write(cr, uid, ids, vals, context=context)
        if need_check:
            if not hasattr(ids, '__iter__'):
                ids = [ids]
            field_to_read = ['categ_ids', 'categ_id'] + [key for key in self._columns if re.match('x_shop.*?_attr_active', key)]
            for product in self.read(cr, uid, ids, field_to_read, context=context):
                product['categ_id'] = product['categ_id'][0]
                self.check_if_activable(cr, uid, product, context=context)
        return res
        
class product_category(Model):
    _inherit = 'product.category'
    
    def check_if_in_shop_category(self, cr, uid, categ_ids, shop_id, context=None):
        exportable_category_ids = self.pool.get('sale.shop').read(cr, uid, shop_id, ['exportable_category_ids'])['exportable_category_ids']
        for categ_id in categ_ids:
            if categ_id in exportable_category_ids:
                return True
        return False
