# -*- encoding: utf-8 -*-
##############################################################################
#
#    product_images_sync module for OpenERP
#    Copyright (C) 2012 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from osv import osv, fields
from base_external_referentials.decorator import only_for_referential, commit_now

# TODO : move field last_images_export_date in this module ? (-> will need to update dependancy ?)

class sale_shop(osv.osv):
    _inherit = 'sale.shop'

    def export_images(self, cr, uid, ids, context=None):
        return self.export_resources(cr, uid, ids, 'product.images', context=context)

sale_shop()

class product_images(osv.osv):
    _inherit = 'product.images'

    @only_for_referential(ref_categ = 'Multichannel Sale')
    def _get_last_exported_date(self, cr, uid, external_session, context=None):
        return self.pool.get('sale.shop').browse(cr, uid, external_session.sync_from_object.id, context=context).last_images_export_date

    @only_for_referential(ref_categ = 'Multichannel Sale')
    @commit_now
    def _set_last_exported_date(self, cr, uid, external_session, date, context=None):
        return self.pool.get('sale.shop').write(cr, uid,
            external_session.sync_from_object.id,
            {'last_images_export_date': date}, context=context)

    def get_ids_and_update_date(self, cr, uid, external_session, ids=None, last_exported_date=None, context=None):
        shop = external_session.sync_from_object
        if shop.exportable_product_ids:
            product_ids = self.pool.get('sale.shop').read(cr, uid, shop.id, ['exportable_product_ids'], context=context)['exportable_product_ids']
            print "product_ids =", product_ids
            image_ids = self.search(cr, uid, [('product_id', 'in', product_ids)], context=context)
            res = super(product_images, self).get_ids_and_update_date(cr, uid, external_session, ids=image_ids, last_exported_date=last_exported_date, context=context)
        else:
            res = (), {}
        return res


product_images()
