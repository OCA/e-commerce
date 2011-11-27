# -*- coding: utf-8 -*-
##############################################################################
#
#    Base_sale_multichannels module for OpenERP
#    Copyright (C) 2010 Sébastien BEAU <sebastien.beau@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import fields,osv
from tools.translate import _

class product_export_wizard(osv.osv_memory):
    _name = 'product.export.wizard'
    _description = 'product export wizard'

    _columns = {
        'shop': fields.many2many('sale.shop', 'shop_rel', 'shop_id', 'product_id', 'Shop', required=True),
        }

    def export(self, cr, uid, id, option, context=None):
        context.update({'force_export':True})
        shop_ids = self.read(cr, uid, id, context=context)[0]['shop']
        sale_shop_obj = self.pool.get('sale.shop')
        product_obj = self.pool.get('product.product')
        context['force_product_ids'] = context['active_ids']
        for shop in sale_shop_obj.browse(cr, uid, shop_ids, context=context):
            context['shop_id'] = shop.id
            if not shop.referential_id:
                raise osv.except_osv(_("User Error"), _("The shop '%s' doesn't have any external referential are you sure that it's an externe sale shop? If yes syncronize it before exporting product")%(shop.name,))
            context['conn_obj'] = shop.referential_id.external_connection()
            none_exportable_product = set(context['force_product_ids']) - set([product.id for product in shop.exportable_product_ids])
            if none_exportable_product:
                products = ', '.join([x['name'] for x in product_obj.read(cr, uid, list(none_exportable_product), fields = ['name'], context=context)])
                raise osv.except_osv(_("User Error"), _("The product '%s' can not be exported to the shop '%s'. \nPlease check : \n    - if their are in the root category \n    - if the website option is correctly configured. \n    - if the check box Magento exportable is checked")%(products, shop.name))
            if option == 'export_product':
                sale_shop_obj.export_products(cr, uid, shop, context)
            elif option == 'export_inventory':
                product_obj.export_inventory(cr, uid, context['force_product_ids'], '', context)
            elif option == 'export_product_and_inventory':
                sale_shop_obj.export_products(cr, uid, shop, context)
                product_obj.export_inventory(cr, uid, context['force_product_ids'], '', context)
            
        return {'type': 'ir.actions.act_window_close'}

    def export_product(self, cr, uid, id,context=None):
        return self.export(cr, uid, id, 'export_product', context)

    def export_inventory(self, cr, uid, id,context=None):
        return self.export(cr, uid, id, 'export_inventory', context)

    def export_product_and_inventory(self, cr, uid, id, context=None):
        return self.export(cr, uid, id, 'export_product_and_inventory', context)



product_export_wizard()
