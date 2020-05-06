# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _get_combination_info(self, combination=False, product_id=False,
                              add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination, product_id, add_qty, pricelist, parent_combination,
            only_template)
        if self.env.context.get('website_sale_stock_get_quantity'):
            product_id = combination_info['product_id']
            if product_id:
                product_obj = self.env['product.product'].sudo()
                product = product_obj.browse(product_id)
                combination_info.update(
                    virtual_available=product.immediately_usable_qty)
        return combination_info
