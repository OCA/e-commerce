# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
from openerp.http import request


class WebSite(orm.Model):
    _inherit = 'website'

    def sale_product_domain(self, cr, uid, ids, context=None):
        domain = super(WebSite, self).sale_product_domain(
            cr, uid, ids=ids, context=context)
        if 'supplier_id' in request.env.context:
            domain.append(
                ('seller_ids.name', '=', request.env.context['supplier_id'])
            )
        return domain
