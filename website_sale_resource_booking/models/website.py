# Copyright 2025 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _lt, models


class Website(models.Model):
    _inherit = "website"

    def _get_checkout_step_list(self):
        steps = super()._get_checkout_step_list()
        order = self.sale_get_order()
        if order.mapped("order_line.product_id.resource_booking_type_id"):
            booking_step_structure = {
                "name": _lt("Schedule bookings"),
                "current_href": "/shop/booking/1/schedule",
                "back_button": _lt("Back to cart"),
                "back_button_href": "/shop/cart",
            }
            steps.insert(
                1, ("website_sale_resource_booking.scheduling", booking_step_structure)
            )
            steps[0][1]["main_button"] = booking_step_structure["name"]
            steps[0][1]["main_button_href"] = booking_step_structure["current_href"]
            steps[2][1]["back_button"] = booking_step_structure["name"]
            steps[2][1]["back_button_href"] = booking_step_structure["current_href"]
        return steps
