# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Follow the field definition as amount_delivery from
    # the website_sale_delivery module.
    amount_payment_fee = fields.Monetary(
        compute="_compute_amount_payment_fee",
        digits=0,
        string="Payment Fee Amount",
        store=True,
        help="Total amount of payment fees applied to this order",
    )

    def _compute_website_order_line(self):
        res = super()._compute_website_order_line()
        for order in self:
            order.website_order_line = order.website_order_line.filtered(
                lambda line: not line.payment_fee_line
            )
        return res

    @api.depends(
        "order_line.price_unit",
        "order_line.tax_id",
        "order_line.discount",
        "order_line.product_uom_qty",
        "order_line.payment_fee_line",
    )
    def _compute_amount_payment_fee(self):
        """Compute the total amount of payment fees in this order."""
        for order in self:
            fee_lines = order.order_line.filtered("payment_fee_line")
            if self.env.user.has_group(
                "account.group_show_line_subtotals_tax_excluded"
            ):
                order.amount_payment_fee = sum(fee_lines.mapped("price_subtotal"))
            else:
                order.amount_payment_fee = sum(fee_lines.mapped("price_total"))

    def _calculate_payment_fee_price(self, provider):
        """Calculate payment fee price according to provider settings."""
        self.ensure_one()
        price = 0.0
        if not provider.charge_fee:
            return price

        if provider.charge_fee_type == "fixed":
            price = provider.charge_fee_fixed_price
            if provider.charge_fee_currency_id != self.pricelist_id.currency_id:
                price = provider.charge_fee_currency_id._convert(
                    price,
                    self.pricelist_id.currency_id,
                    self.company_id,
                    self.date_order,
                )
        elif provider.charge_fee_type == "percentage":
            # Calculate amount excluding existing payment fees
            base_amount = self.amount_total
            existing_fees = sum(
                self.order_line.filtered("payment_fee_line").mapped("price_total")
            )
            base_amount -= existing_fees
            price = (provider.charge_fee_percentage / 100.0) * base_amount

        return price

    def update_fee_line(self, provider):
        """Update payment fee line based on the selected payment provider."""
        self.ensure_one()
        # Remove existing fee lines
        fee_lines = self.order_line.filtered("payment_fee_line")
        if fee_lines:
            fee_lines.unlink()

        price = self._calculate_payment_fee_price(provider)
        if price <= 0:
            return

        self.env["sale.order.line"].create(
            {
                "order_id": self.id,
                "payment_fee_line": True,
                "product_id": provider.charge_fee_product_id.id,
                "product_uom": provider.charge_fee_product_id.uom_id.id,
                "name": provider.charge_fee_description,
                "price_unit": price,
                "product_uom_qty": 1,
            }
        )
