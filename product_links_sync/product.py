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

from datetime import datetime

from openerp.osv.orm import Model
from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from base_external_referentials.decorator import only_for_referential
from base_external_referentials.decorator import commit_now


class product_product(Model):
    _inherit = "product.product"

    _columns = {
        'product_link_write_last_date': fields.datetime('Product Link Last Write Date'),
    }

    def _update_product_link_last_date(self, cr, uid, vals, context=None):
        if 'product_link_ids' in vals:
            vals['product_link_write_last_date'] = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return vals

    def create(self, cr, uid, vals, context=None):
        vals = self._update_product_link_last_date(cr, uid, vals, context=context)
        return super(product_product, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context={}
        vals = self._update_product_link_last_date(cr, uid, vals, context=context)
        ctx = context.copy()
        ctx['product_link_date_updated'] = True
        return super(product_product, self).write(cr, uid, ids, vals, context=ctx)

    def _get_query_and_params_for_ids_and_date(self, cr, uid, external_session, ids=None, last_exported_date=None, context=None):
        if context.get('export_product') != 'link':
            return super(product_product, self)._get_query_and_params_for_ids_and_date(cr, uid,
                        external_session, ids=ids, last_exported_date=last_exported_date, context=context)
        else:
            # We have to export all product link that believe to a product which have the link modify
            # or have been created in the external system since the last export
            params = ()
            query = """
                SELECT GREATEST(product_link_write_last_date, ir_model_data.create_date) as update_date,
                    product_product.id as id, ir_model_data.res_id, product_link_write_last_date
                    FROM product_product
                LEFT JOIN ir_model_data
                    ON product_product.id = ir_model_data.res_id
                    AND ir_model_data.model = 'product.product'
                    AND ir_model_data.module = 'extref/%(ref_name)s'
                WHERE product_link_write_last_date is not NULL
                """%{
                        'ref_name': external_session.referential_id.name,
                }
            if ids:
                query += " AND product_product.id in %s"
                params += (tuple(ids),)
            if last_exported_date:
                query += " AND (GREATEST(product_link_write_last_date,ir_model_data.create_date) > %s)"
                params += (last_exported_date,)

            return query, params

    def get_field_to_export(self, cr, uid, ids, mapping, mapping_id, context=None):
        fields_to_read = super(product_product, self).get_field_to_export(cr, uid, ids, mapping, mapping_id, context=context)
        if context.get('export_product') == 'link':
            fields_to_read = ['product_link_ids']
        else:
            if 'product_link_ids' in fields_to_read: fields_to_read.remove('product_link_ids')
        return fields_to_read

    @only_for_referential(ref_categ ='Multichannel Sale')
    def _get_last_exported_date(self, cr, uid, external_session, context):
        shop = external_session.sync_from_object
        if context.get('export_product') == 'link':
            return shop.last_products_links_export_date
        else:
            return super(product_product, self)._get_last_exported_date(cr, uid, external_session, context)

    @only_for_referential(ref_categ ='Multichannel Sale')
    @commit_now
    def _set_last_exported_date(self, cr, uid, external_session, date, context):
        shop = external_session.sync_from_object
        if context.get('export_product') == 'link':
            return self.pool.get('sale.shop').write(cr, uid, shop.id, {'last_products_links_export_date': date}, context=context)
        else:
            return super(product_product, self)._set_last_exported_date(cr, uid, external_session, date, context)


class product_link(Model):
    _inherit = "product.link"

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context={}
        if 'is_active' in vals and not context.get('product_link_date_updated'):
            for link in self.browse(cr, uid, ids, context=context):
                link.product_id.write(
                    {'product_link_write_last_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)},
                    context=context)
        return super(product_link, self).write(cr, uid, ids, vals, context=context)


class product_export_wizard(TransientModel):
    _inherit = 'product.export.wizard'

    def _export_one_product(self, cr, uid, external_session, product_id, options, context=None):
        res = super(product_export_wizard, self)._export_one_product(cr, uid, external_session, product_id, options, context=context)
        if 'export_link' in options:
            context['export_product'] = 'link'
            self.pool.get('product.product')._export_one_resource(cr, uid, external_session, product_id, context=context)
        return res

    def _get_all_options(self, cr, uid, context=None):
        res = super(product_export_wizard, self)._get_all_options(cr, uid, context=context)
        res.append('export_link')
        return res


