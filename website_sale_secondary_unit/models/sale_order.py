# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools.float_utils import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_add(self, product_id, quantity=1.0, *, uom_id=None, **kwargs):
        """Convert the quantity, expressed in secondary units, to the product one.

        The frontend sends the quantity in the unit chosen by the customer along
        with the corresponding ``secondary_uom_id``. Products that can't be sold
        in their own unit fall back to their default secondary unit when none is
        received (e.g. the "Add to cart" snippet or an express checkout).

        Callers that already know the quantity in the product unit of measure,
        like the portal reorder, send it along with the secondary unit of the
        original line setting ``qty_in_secondary_uom`` to ``False``, so neither
        the conversion nor the default secondary unit are applied to it.
        """
        qty_in_secondary_uom = kwargs.pop("qty_in_secondary_uom", True)
        if kwargs.get("linked_line_id"):
            # `/shop/cart/add` forwards the values of the main product to the
            # `_cart_add` call of its optional products, which are always added
            # in their own unit of measure.
            kwargs.pop("secondary_uom_id", None)
        product = self.env["product.product"].browse(product_id)
        if (
            product
            and qty_in_secondary_uom
            and "secondary_uom_id" not in kwargs
            and not product.allow_uom_sell
        ):
            secondary_uom = (
                product.sale_secondary_uom_id
                or product._get_website_secondary_uoms()[:1]
            )
            kwargs["secondary_uom_id"] = secondary_uom.id
        secondary_uom_id = int(kwargs.get("secondary_uom_id") or 0)
        if secondary_uom_id and qty_in_secondary_uom:
            secondary_uom = self.env["product.secondary.unit"].browse(secondary_uom_id)
            quantity = float_round(
                quantity * secondary_uom.factor,
                precision_rounding=product.uom_id.rounding,
            )
        return super()._cart_add(product_id, quantity, uom_id=uom_id, **kwargs)

    def _cart_find_product_line(
        self, product_id, uom_id, secondary_uom_id=None, **kwargs
    ):
        """Only merge cart lines sharing the same secondary unit."""
        so_lines = super()._cart_find_product_line(product_id, uom_id, **kwargs)
        if not so_lines:
            return so_lines
        secondary_uom_id = int(secondary_uom_id) if secondary_uom_id else False
        return so_lines.filtered(
            lambda sol: sol.secondary_uom_id.id == secondary_uom_id
        )

    def _prepare_order_line_values(
        self, product_id, quantity, uom_id, *, secondary_uom_id=None, **kwargs
    ):
        values = super()._prepare_order_line_values(
            product_id, quantity, uom_id, **kwargs
        )
        values["secondary_uom_id"] = (
            int(secondary_uom_id) if secondary_uom_id else False
        )
        return values

    def _prepare_order_line_update_values(self, order_line, quantity, **kwargs):
        values = super()._prepare_order_line_update_values(
            order_line, quantity, **kwargs
        )
        # Only touch the secondary unit when the caller explicitly sent one,
        # otherwise a plain quantity update from the cart would clear it.
        if "secondary_uom_id" in kwargs:
            secondary_uom_id = (
                int(kwargs["secondary_uom_id"]) if kwargs["secondary_uom_id"] else False
            )
            if secondary_uom_id != order_line.secondary_uom_id.id:
                values["secondary_uom_id"] = secondary_uom_id
        return values

    def _compute_cart_info(self):
        """Count lines sold in secondary units as secondary units."""
        res = super()._compute_cart_info()
        for order in self:
            secondary_unit_lines = order.website_order_line.filtered("secondary_uom_id")
            if secondary_unit_lines:
                other_lines = order.website_order_line - secondary_unit_lines
                order.cart_quantity = int(
                    sum(other_lines.mapped("product_uom_qty"))
                    + sum(secondary_unit_lines.mapped("secondary_uom_qty"))
                )
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_displayed_quantity(self):
        """Show (and let the customer edit) the quantity in secondary units."""
        self.ensure_one()
        if not self.secondary_uom_id:
            return super()._get_displayed_quantity()
        rounded_qty = round(
            self.secondary_uom_qty,
            self.env["decimal.precision"].precision_get("Product Unit"),
        )
        return int(rounded_qty) if int(rounded_qty) == rounded_qty else rounded_qty
