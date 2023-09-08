# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_contract_product_in_cart(self):
        return self.order_line.product_id.filtered(lambda product: product.is_contract)

    def _cart_update(
        self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs
    ):
        """Remove unwanted order lines from cart."""
        values = super(SaleOrder, self)._cart_update(
            product_id, line_id, add_qty, set_qty, **kwargs
        )
        product = self.env["product.product"].browse(product_id)
        order_line = self.env["sale.order.line"]
        if product:
            contract_product_in_order_line = self._get_contract_product_in_cart()
            if (
                product.is_contract
                and contract_product_in_order_line
                and product != contract_product_in_order_line[0]
            ):
                # If contracted products are available in the cart, remove other
                # contract products from the cart
                order_line = self.order_line.filtered(lambda x: x.product_id == product)
            elif (
                contract_product_in_order_line and not product.is_contract
            ) or product.is_contract:
                # If any non-contracted products available in the cart, remove those
                # products from the cart
                order_line = self.order_line.filtered(
                    lambda x: not x.product_id.is_contract
                )
        if order_line:
            order_line.unlink()
        return values

    def _verify_updated_quantity(self, order_line, product_id, new_qty, **kwargs):
        """Forbid quantity update on contract product lines and restrict purchase of
        non contract products with contract products and allow purchase of only a
        single contract product at a time."""
        product = self.env["product.product"].browse(product_id)
        contract_product_in_order_line = self._get_contract_product_in_cart()
        if contract_product_in_order_line and not product.is_contract and new_qty > 0:
            return 0, _(
                "Important Notice: It is not possible to make a purchase that includes"
                " both a contract and a regular product simultaneously.Please purchase"
                " these separately."
            )
        elif product.is_contract:
            if (
                contract_product_in_order_line
                and product != contract_product_in_order_line[0]
            ):
                return 0, _(
                    "Important Notice: There's already another contract product in the"
                    " cart, you can purchase only one contract product at a time"
                )
            else:
                warning_msg = ""
                if new_qty > 1:
                    warning_msg = (
                        "Important Notice: You cannot have quantity more than 1 for "
                        "contract product in the cart!"
                    )
                order_line = self.order_line.filtered(
                    lambda x: not x.product_id.is_contract
                )
                if order_line:
                    if warning_msg:
                        warning_msg += (
                            "Also,your previous cart items are removed from your cart"
                            " as you are buying a contract product!"
                        )
                    else:
                        warning_msg = (
                            "Important Notice: Your previous cart items are removed "
                            "from your cart as you are buying a contract product!"
                        )
                if warning_msg:
                    return 1, _(warning_msg)
        return super()._verify_updated_quantity(
            order_line, product_id, new_qty, **kwargs
        )
