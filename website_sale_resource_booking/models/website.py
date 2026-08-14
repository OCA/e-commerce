# Copyright 2025 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    def _get_allowed_steps_domain(self):
        domain = super()._get_allowed_steps_domain()
        if (
            not request.cart
            or not request.cart.order_line.product_id.resource_booking_type_id
        ):
            domain.append(("step_href", "!=", "/shop/booking/1/schedule"))
        return domain
