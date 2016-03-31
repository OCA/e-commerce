# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import model
from openerp.http import request


class WebSite(models.Model):
    _inherit = 'website'

    def sale_product_domain(self, cr, uid, ids, context=None):
        domain = super(WebSite, self).sale_product_domain(cr, uid, ids=ids,
                                                          context=context)
        if 'brand_id' in request.context:
            domain.append(
                ('product_brand_id', '=', request.context['brand_id']))
        return domain
