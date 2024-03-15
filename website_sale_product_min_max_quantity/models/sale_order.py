# Copyright 2023 Binhex - Nicolás Ramos <n.ramos@binhex.cloud>
# Copyright 2023 Binhex - Adasat Torres <a.torres@binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _verify_updated_quantity(self, order_line, product_id, new_qty, **kwargs):
        product = self.env["product.product"].browse(int(product_id))
        if float(new_qty) > product.website_sale_max_qty:
            return product.website_sale_max_qty, "maxquantity"
        return super()._verify_updated_quantity(
            order_line, product_id, new_qty, **kwargs
        )
