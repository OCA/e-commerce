# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_next_provisioning_date = fields.Boolean(
        help="Shows the next provisioning date in the website shop "
             "if the product is out of stock. This option may not make "
             "sense if you don't select an 'Availability' option that "
             "shows the inventory of the product in the website shop."
    )

    def _get_next_provisioning_date(self):
        return self.product_variant_ids._get_next_provisioning_date()

    @api.multi
    def _get_combination_info(self, combination=False, product_id=False,
                              add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )
        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(
                combination_info['product_id'])
        else:
            product = self.sudo()
        provisioning_date = False
        if (product.show_next_provisioning_date
                and product.qty_available - product.outgoing_qty <= 0):
            provisioning_date = product._get_next_provisioning_date()
        combination_info.update(provisioning_date=provisioning_date)
        return combination_info
