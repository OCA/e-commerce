# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, uom, date, website
    ):
        combination_info = super()._get_additionnal_combination_info(
            product_or_template, quantity, uom, date, website
        )
        template = (
            product_or_template
            if product_or_template._name == "product.template"
            else product_or_template.product_tmpl_id
        )
        if not template._has_multiple_uoms():
            return combination_info
        pricelist = request.pricelist.with_context(**self.env.context)
        combination_info["packaging_prices"] = {}
        for product_uom in template._get_available_uoms():
            # Unit price expressed in the packaging UoM...
            uom_price = pricelist._get_product_price(
                product=product_or_template, quantity=quantity, uom=product_uom
            )
            # ...converted back to the product base UoM, as displayed prices are.
            combination_info["packaging_prices"][product_uom.id] = (
                product_uom._compute_price(
                    price=uom_price, to_unit=product_or_template.uom_id
                )
            )
        return combination_info
