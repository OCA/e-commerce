# -*- coding: utf-8 -*-
##############################################################################
#
#    Base sale export product module for OpenERP
#    Copyright (C) 2010-2012 Sébastien BEAU <sebastien.beau@akretion.com>
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


from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from base_external_referentials.external_osv import ExternalSession

class product_export_wizard(TransientModel):
    _name = 'product.export.wizard'
    _description = 'product export wizard'

    _columns = {
        'shop': fields.many2many('sale.shop', 'shop_rel', 'shop_id', 'product_id', 'Shop', required=True),
        }

    def _export_one_product(self, cr, uid, external_session, product_id, options, context=None):
        product_obj = self.pool.get('product.product')
        if 'export_product' in options:
            product_obj._export_one_resource(cr, uid, external_session, product_id, context=context)
        if 'export_inventory' in options:
            product_obj.export_inventory(cr, uid, external_session, [product_id], context=context)
        if 'export_image' in options:
            product_obj.export_product_images(cr, uid, external_session, [product_id], context=context)
        return True

    def export(self, cr, uid, id, options, context=None):
        if context is None:
            context={}
        shop_ids = self.read(cr, uid, id, context=context)[0]['shop']
        sale_shop_obj = self.pool.get('sale.shop')
        product_obj = self.pool.get('product.product')
        product_ids = context['active_ids']

        for shop in sale_shop_obj.browse(cr, uid, shop_ids, context=context):
            if not shop.referential_id:
                raise except_osv(_("User Error"),
				_("The shop '%s' doesn't have any external "
                              	"referential are you sure that it's an external sale shop? "
                              	"If yes syncronize it before exporting product")%(shop.name,))
            external_session = ExternalSession(shop.referential_id, shop)
            context = sale_shop_obj.init_context_before_exporting_resource(cr, uid, external_session, shop.id, 'product.product', context=context)
            none_exportable_product = set(product_ids) - set([product.id for product in shop.exportable_product_ids])
            if none_exportable_product:
                products = ', '.join([x['name'] for x in product_obj.read(cr, uid, list(none_exportable_product), fields = ['name'], context=context)])
                raise except_osv(_("User Error"),
                        _("The product '%s' can not be exported to the shop '%s'. \n"
                        "Please check : \n"
                        "    - if they are in the root category \n"
                        "    - if the website option is correctly configured. \n"
                        "    - if the check box to export the product to the shop is checked")%(products, shop.name))
            for product_id in product_ids:
                self._export_one_product(cr, uid, external_session, product_id, options, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def export_product(self, cr, uid, id, context=None):
        return self.export(cr, uid, id, ['export_product'], context)

    def export_inventory(self, cr, uid, id, context=None):
        return self.export(
            cr, uid, id, ['export_inventory'], context)

    def export_image(self, cr, uid, id, context=None):
        return self.export(
            cr, uid, id, ['export_image'], context)

    def _get_all_options(self, cr, uid, context=None):
        return ['export_product', 'export_inventory', 'export_image']

    def export_all(self, cr, uid, id, context=None):
        return self.export(cr, uid, id, self._get_all_options(cr, uid, context=context), context)
