from odoo import api, fields, models
from odoo.exceptions import UserError


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = "choose.delivery.carrier"

    saleor_warning_msg = fields.Text(compute="_compute_saleor_support")

    @api.depends(
        "carrier_id",
        "total_weight",
        "order_id.amount_total",
        "order_id.saleor_channel_id",
    )
    def _compute_saleor_support(self):
        for wizard in self:
            wizard.saleor_warning_msg = ""
            carrier = wizard.carrier_id
            lines = carrier.saleor_order_value_line_ids
            if carrier.shipping_method_type == "weight":
                for line in lines:
                    if wizard.total_weight > line.max_value:
                        wizard.saleor_warning_msg = wizard.env._(
                            "The total weight of the order exceeds"
                            " the maximum weight for this carrier."
                        )
            elif carrier.shipping_method_type == "price":
                for line in lines:
                    if wizard.order_id.amount_total > line.max_value:
                        wizard.saleor_warning_msg = wizard.env._(
                            "The total amount of the order exceeds"
                            " the maximum amount for this carrier."
                        )
            else:
                wizard.saleor_warning_msg = ""

    @api.onchange("carrier_id", "total_weight")
    def _onchange_carrier_id(self):
        self.delivery_message = False
        if self.delivery_type in ("fixed", "base_on_rule", "saleor"):
            vals = self._get_delivery_rate()
            if vals.get("error_message"):
                return {"error": vals["error_message"]}
        else:
            self.display_price = 0
            self.delivery_price = 0

    def _get_delivery_rate(self):
        self.ensure_one()

        if self.delivery_type == "saleor":
            order = self.order_id
            saleor_channel = order.saleor_channel_id
            carrier = self.carrier_id

            order.saleor_delivery_carrier_id = carrier.id

            if not saleor_channel:
                raise UserError(
                    self.env._("This order does not have a Saleor channel linked.")
                )

            price_line = carrier.saleor_shipping_pricing_line_ids.filtered(
                lambda line: line.channel_id == saleor_channel
            )

            if not price_line:
                raise UserError(
                    self.env._(
                        "No shipping price configured for channel '%s'.",
                        saleor_channel.name,
                    )
                )

            price = price_line[0].price
            self.delivery_price = price
            self.display_price = price
            self.delivery_message = self.env._(
                "Saleor shipping via channel: %s", saleor_channel.name
            )

            return {"success": True, "no_rate": False}

        return super()._get_delivery_rate()
