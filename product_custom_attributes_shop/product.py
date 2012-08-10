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

from osv import osv, fields
import netsvc
from lxml import etree
from tools.translate import _

class product_product(osv.osv):

    _inherit = "product.product"

    _columns = {
    }

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
        return result
