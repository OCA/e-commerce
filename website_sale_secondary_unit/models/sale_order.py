# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.http import request
from odoo.tools.float_utils import float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        """
        Search sale order lines with secondary units
        """
        so_lines = super()._cart_find_product_line(
            product_id=product_id, line_id=line_id, **kwargs
        )
        if so_lines:
            if line_id:
                sol = self.env["sale.order.line"].browse(line_id)
                secondary_uom_id = sol.secondary_uom_id.id
            else:
                secondary_uom_id = self.env.context.get("secondary_uom_id", False)
            so_lines = so_lines.filtered(
                lambda x: x.secondary_uom_id.id == secondary_uom_id
            )
        return so_lines

    def _website_product_id_change(self, order_id, product_id, qty=0, **kwargs):
        res = super()._website_product_id_change(
            order_id, product_id, qty=qty, **kwargs
        )
        secondary_uom_id = self.env.context.get("secondary_uom_id", False)
        res["secondary_uom_id"] = secondary_uom_id
        return res

    def _cart_update(
        self,
        product_id=None,
        line_id=None,
        add_qty=0,
        set_qty=0,
        attributes=None,
        **kwargs
    ):
        if line_id:
            sol = self.env["sale.order.line"].browse(line_id)
            secondary_uom_id = sol.secondary_uom_id.id
        else:
            secondary_uom_id = request.session.get("secondary_uom_id", False)
        self.env.context.copy()
        if not secondary_uom_id:
            # Check the default value for secondary uom or is a product can
            # not allow to sell in base unit, so the default secondary uom
            # will be the first secondary uom record.
            product = self.env["product.product"].browse(product_id)
            if not product.allow_uom_sell:
                secondary_uom = (
                    product.sale_secondary_uom_id or product.secondary_uom_ids[:1]
                )
                if secondary_uom and add_qty:
                    add_qty = float_round(
                        float(add_qty) * secondary_uom.factor,
                        precision_rounding=secondary_uom.uom_id.rounding,
                    )
                    secondary_uom_id = secondary_uom.id
        return super(
            SaleOrder, self.with_context(secondary_uom_id=secondary_uom_id)
        )._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=attributes,
            **kwargs
        )

    def _compute_cart_info(self):
        res = super()._compute_cart_info()
        for order in self:
            secondary_unit_lines = order.website_order_line.filtered("secondary_uom_id")
            if secondary_unit_lines:
                cart_secondary_quantity = int(
                    sum(secondary_unit_lines.mapped("secondary_uom_qty"))
                )
                so_lines = order.website_order_line - secondary_unit_lines
                cart_quantity = int(sum(so_lines.mapped("product_uom_qty")))
                order.cart_quantity = cart_quantity + cart_secondary_quantity
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        SecondaryUom = self.env["product.secondary.unit"]
        Uom = self.env["uom.uom"]
        for vals in vals_list:
            secondary_uom = SecondaryUom.browse(vals.get("secondary_uom_id", False))
            uom = Uom.browse(vals.get("product_uom", False))
            if secondary_uom:
                factor = secondary_uom.factor * (uom.factor or 1.0)
                vals["secondary_uom_qty"] = float_round(
                    vals["product_uom_qty"] / (factor or 1.0),
                    precision_rounding=secondary_uom.uom_id.rounding,
                )
        return super().create(vals_list)

    def write(self, vals):
        SecondaryUom = self.env["product.secondary.unit"]
        Uom = self.env["uom.uom"]
        for line in self:
            secondary_uom = (
                "secondary_uom_id" in vals
                and SecondaryUom.browse(vals["secondary_uom_id"])
                or line.secondary_uom_id
            )
            uom = (
                "product_uom" in vals
                and Uom.browse(vals["product_uom"])
                or line.product_uom
            )
            if (
                "product_uom_qty" in vals
                and secondary_uom
                and secondary_uom.dependency_type == "dependent"
            ):
                factor = secondary_uom.factor * uom.factor
                vals["secondary_uom_qty"] = float_round(
                    vals["product_uom_qty"] / (factor or 1.0),
                    precision_rounding=secondary_uom.uom_id.rounding,
                )
        return super().write(vals)
