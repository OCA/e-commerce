# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class WebSite(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_product_domain(self):
        domain = super(WebSite, self).sale_product_domain()
        if 'brand_id' in self.env.context:
            domain.append(
                ('product_brand_id', '=', self.env.context['brand_id']))
        return domain
