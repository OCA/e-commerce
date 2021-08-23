# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.osv import expression


class Website(models.Model):
    _inherit = "website"

    cart_expire_delay = fields.Float(
        string="Expire Delay",
        default=0.0,
        help="Automatically cancel website orders after the given time.\n"
        "Set to 0 to disable this feature.",
    )

    def _get_cart_expire_delay_domain(self):
        self.ensure_one()
        expire_date = fields.Datetime.now() - timedelta(hours=self.cart_expire_delay)
        return [
            ("website_id", "=", self.id),
            ("state", "in", ["draft", "sent"]),
            ("write_date", "<=", expire_date),
        ]

    @api.model
    def _scheduler_website_expire_cart(self):
        websites = self.search([("cart_expire_delay", ">", 0)])
        if not websites:
            return True
        # Get all carts to expire
        carts_to_expire_domains = [
            website._get_cart_expire_delay_domain() for website in websites
        ]
        carts_to_expire = self.env["sale.order"].search(
            expression.OR(carts_to_expire_domains)
        )
        # Expire carts
        for cart in carts_to_expire:
            cart.message_post(body=_("Cart expired"))
        carts_to_expire.action_cancel()
