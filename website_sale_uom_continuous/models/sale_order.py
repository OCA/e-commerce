# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _compute_cart_info(self):
        # OVERRIDE: count each line in a continuous UoM (e.g. 2.5 kg) as one item.
        # Only the difference with the core quantity (the sum of all quantities) is
        # applied, to keep the adjustments made by other modules.
        res = super()._compute_cart_info()
        for order in self:
            lines = order.website_order_line
            continuous_lines = lines.filtered(
                lambda line: line.product_uom_id._is_continuous()
            )
            if not continuous_lines:
                continue
            other_lines = lines - continuous_lines
            core_quantity = int(sum(lines.mapped("product_uom_qty")))
            quantity = int(sum(other_lines.mapped("product_uom_qty"))) + len(
                continuous_lines.filtered(lambda line: line.product_uom_qty > 0)
            )
            order.cart_quantity += quantity - core_quantity
        return res

    def _cart_add(self, product_id, quantity=1.0, *, uom_id=None, **kwargs):
        # OVERRIDE: core casts the requested quantity to an integer in the
        # controller. Use the one handed over through the context instead, for the
        # main product in a continuous UoM (see the cart controller).
        requested_qty = self.env.context.get("website_sale_uom_continuous_add_qty", {})
        if product_id in requested_qty and not kwargs.get("linked_line_id"):
            product = self.env["product.product"].browse(product_id)
            uom = product.uom_id
            if uom_id in product.product_tmpl_id._get_available_uoms().ids:
                uom = self.env["uom.uom"].browse(uom_id)
            if uom._is_continuous():
                quantity = uom.round(requested_qty[product_id])
        return super()._cart_add(product_id, quantity=quantity, uom_id=uom_id, **kwargs)

    def _cart_update_line_quantity(self, line_id, quantity, **kwargs):
        # OVERRIDE: core casts the requested quantity to an integer in the
        # controller. Use the one handed over through the context instead, for a
        # line in a continuous UoM (see the cart controller).
        requested_qty = self.env.context.get(
            "website_sale_uom_continuous_update_qty", {}
        )
        # Read before calling super, which deletes the line when its quantity is 0
        uom = self.order_line.filtered(lambda sol: sol.id == line_id).product_uom_id
        if line_id in requested_qty and uom._is_continuous():
            quantity = uom.round(requested_qty[line_id])
        values = super()._cart_update_line_quantity(line_id, quantity, **kwargs)
        # Core computes the added quantity as new_qty - old_qty, which leaks
        # floating point noise with decimals (e.g. 3.6 - 2.5 = 1.1000000000000005).
        if uom and "added_qty" in values:
            values["added_qty"] = uom.round(values["added_qty"])
        return values
