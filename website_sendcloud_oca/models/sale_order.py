# Copyright 2025 Onestein (<https://www.onestein.nl>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_delivery_methods(self):
        return super(
            SaleOrder, self.with_context(sale_order_id=self.id)
        )._get_delivery_methods()

    def sendcloud_sale_delivery_data(self, carrier):
        self.ensure_one()
        self.write({"sendcloud_service_point_address": False})
        return {
            "sendcloud_details": {
                "order_id": self.id,
                "key": carrier.sendcloud_integration_id.public_key or "",
                "country_code": self.partner_shipping_id.country_id.code or "",
                "postcode": self.partner_id.zip or "",
                "carrier_name": [carrier.sendcloud_carrier or ""],
            }
        }

    def _check_carrier_quotation(self, force_carrier_id=None, keep_carrier=False):
        self.ensure_one()
        if (
            not force_carrier_id
            and self.partner_shipping_id.property_delivery_carrier_id
            and not keep_carrier
        ):
            force_carrier_id = self.partner_shipping_id.property_delivery_carrier_id.id
        carrier = (
            force_carrier_id
            and self.env["delivery.carrier"].browse(force_carrier_id)
            or self.carrier_id
        )
        if carrier:
            res = carrier.rate_shipment(self)
            if res.get("sendcloud_country_specific_product"):
                self = self.with_context(
                    sendcloud_country_specific_product=res[
                        "sendcloud_country_specific_product"
                    ]
                )
        return super()._check_carrier_quotation(
            force_carrier_id=force_carrier_id, keep_carrier=keep_carrier
        )
