from odoo import fields, models


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    cart_quantity = fields.Float(
        compute="_compute_cart_info",
    )

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        if (
            (isinstance(add_qty, int) or isinstance(set_qty, int))
            and add_qty is not False
            and set_qty is not False
        ):
            return super()._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        else:
            # Add or set product quantity, add_qty can be negative
            self.ensure_one()
            self = self.with_company(self.company_id)

            # if self.state != "draft":
            #     self.env["request"].session.pop("sale_order_id", None)
            #     self.env["request"].session.pop("website_sale_cart_quantity", None)

            self.env["product.product"].browse(product_id).exists()

            if line_id is not False:
                order_line = self._cart_find_product_line(
                    product_id, line_id, **kwargs
                )[:1]
            else:
                order_line = self.env["sale.order.line"]

            quantity = 0
            if set_qty:
                quantity = set_qty
            elif add_qty:
                if order_line:
                    quantity = order_line.product_uom_qty + add_qty
                else:
                    quantity = add_qty

            warning = ""

            if quantity > 0:
                quantity, warning = self._verify_updated_quantity(
                    order_line,
                    product_id,
                    quantity,
                    **kwargs,
                )

            # Round it to avoid infinite 0 with a one after it
            quantity = round(quantity, 9)

            order_line = self._cart_update_order_line(
                product_id, quantity, order_line, **kwargs
            )

            return {
                "line_id": order_line.id,
                "quantity": quantity,
                "option_ids": list(
                    set(
                        order_line.option_line_ids.filtered(
                            lambda line: line.order_id == order_line.order_id
                        ).ids
                    )
                ),
                "warning": warning,
            }

    def _compute_cart_info(self):
        all_sums_are_int = True
        for order in self:
            total_quantity = sum(order.mapped("website_order_line.product_uom_qty"))

            if not isinstance(total_quantity, int):
                all_sums_are_int = False

            only_services = all(
                line.product_id.type == "service" for line in order.website_order_line
            )
            order.only_services = only_services
        if all_sums_are_int:
            return super()._compute_cart_info()
        else:
            for order in self:
                order.cart_quantity = sum(
                    order.mapped("website_order_line.product_uom_qty")
                )
                order.only_services = all(
                    line.product_id.type == "service"
                    for line in order.website_order_line
                )
