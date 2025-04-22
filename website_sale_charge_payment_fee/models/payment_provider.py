# Copyright 2018 Lorenzo Battistini - Agile Business Group
# Copyright 2020 AITIC S.A.S
# Copyright 2020 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    charge_fee = fields.Boolean(
        "Fee charged to customer",
        help="An extra fee line will be added to online order when using this "
        "payment method",
    )
    charge_fee_description = fields.Text("Fee Description")
    charge_fee_product_id = fields.Many2one("product.product", string="Fee Product")
    charge_fee_fixed_price = fields.Float(
        "Fixed Price",
        digits="Product Price",
    )
    charge_fee_currency_id = fields.Many2one("res.currency", string="Fee Currency")
    charge_fee_percentage = fields.Float(
        "Percentage", help="Percentage applied to order total"
    )
    charge_fee_type = fields.Selection(
        [("fixed", "Fixed"), ("percentage", "Percentage")],
        string="Computation type",
        default="fixed",
    )

    @api.onchange("charge_fee_product_id")
    def onchange_charge_fee_product_id(self):
        if self.charge_fee_product_id:
            self.charge_fee_description = self.charge_fee_product_id.name

    def _calculate_payment_fee_price(self, amount_total):
        """Calculate payment fee price according to provider settings."""
        self.ensure_one()
        price = 0.0
        if not self.charge_fee:
            return price

        if self.charge_fee_type == "fixed":
            price = self.charge_fee_fixed_price
            price = self.charge_fee_currency_id._convert(
                price,
                self.charge_fee_currency_id,
                self.company_id,
                fields.Date.today(),
            )
        elif self.charge_fee_type == "percentage":
            # Calculate amount excluding existing payment fees
            price = (self.charge_fee_percentage / 100.0) * amount_total
        return price
