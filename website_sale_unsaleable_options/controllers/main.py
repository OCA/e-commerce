# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import http
from odoo.addons.website_sale_options.controllers.main import (
    WebsiteSaleOptions)
from odoo.http import request
from odoo.tools.translate import _


class WebsiteSaleUnsalableOptions(WebsiteSaleOptions):
    @http.route()
    def modal(self, product_id, **kw):
        """Render warning if product is optional.

        `optional_product_ids` is saved on product.template.
        However, the AJAX request sends the product_id saved
        on product.product! Since these 2 IDs can vary, we have
        to consider such cases here.

         :param int product_id:
            Product ID (product.product) of item in question.
        """
        # get corresponding product template id
        prod_tmpl_id = request.env['product.product'].browse(
            product_id).product_tmpl_id.id

        product_context = dict(request.context)
        product_context.update(kw.get('kwargs', {}).get('context', {}))

        template = request.env['product.template']
        prod_ids = template.with_context(product_context).search(
            [('optional_product_ids', 'in', [prod_tmpl_id])])

        if prod_ids:
            products = template.with_context(product_context).browse(
                int(prod_ids))
            prod_list = [p.name for p in products]
            message = _("You can't direcly add to cart an optional "
                        "product. You should first add one of the "
                        "following products: "
                        "%s") % '; '.join(prod_list)
            return request.env['ir.ui.view'].render_template(
                "website_sale_unsaleable_options.modal_warning", {
                    'message': message,
                })
        else:
            return super(WebsiteSaleUnsalableOptions, self).modal(
                product_id, **kw)
