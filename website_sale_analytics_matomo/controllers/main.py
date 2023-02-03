# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleMatomo(WebsiteSale):
    def order_2_return_dict(self, order):
        """Adapts the tracking_cart dict of the order for Matomo analytics"""
        ret = super().order_2_return_dict(order)
        ret["order_name"] = order.name
        ret["subtotal"] = order.amount_untaxed
        return ret
