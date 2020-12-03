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
        track_visibility="always",
    )

    @api.one
    def _compute_website_order_line(self):
        super(SaleOrder, self)._compute_website_order_line()
        self.website_order_line = self.website_order_line.filtered(
            lambda l: not l.payment_fee_line
        )

    @api.depends(
        "order_line.price_unit",
        "order_line.tax_id",
        "order_line.discount",
        "order_line.product_uom_qty",
    )
    def _compute_amount_payment_fee(self):
        for order in self:
            if self.env.user.has_group(
                "account.group_show_line_subtotals_tax_excluded"
            ):
                order.amount_payment_fee = sum(
                    order.order_line.filtered("payment_fee_line").mapped(
                        "price_subtotal"
                    )
                )
            else:
                order.amount_payment_fee = sum(
                    order.order_line.filtered("payment_fee_line").mapped("price_total")
                )

    def update_fee_line(self, acquirer):
        self.ensure_one()
        for line in self.order_line:
            if line.payment_fee_line:
                line.unlink()
        if acquirer.charge_fee:
            if acquirer.charge_fee_type == "fixed":
                price = acquirer.charge_fee_fixed_price
                if (
                    acquirer.charge_fee_currency_id.id
                    != self.pricelist_id.currency_id.id
                ):
                    price = acquirer.charge_fee_currency_id._convert(
                        price,
                        self.pricelist_id.currency_id,
                        self.company_id,
                        self.date_order,
                    )
            elif acquirer.charge_fee_type == "percentage":
                price = (acquirer.charge_fee_percentage / 100.0) * self.amount_total
            self.env["sale.order.line"].create(
                {
                    "order_id": self.id,
                    "payment_fee_line": True,
                    "product_id": acquirer.charge_fee_product_id.id,
                    "product_uom": acquirer.charge_fee_product_id.uom_id.id,
                    "name": acquirer.charge_fee_description,
                    "price_unit": price,
                    "product_uom_qty": 1,
                }
            )
