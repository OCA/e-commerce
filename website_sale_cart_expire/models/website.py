# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


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
            ("state", "=", "draft"),
            ("write_date", "<=", expire_date),
            # We don't want to cancel carts that are already in payment.
            "|",
            ("transaction_ids", "=", False),
            "!",
            ("transaction_ids.state", "in", ["pending", "authorized", "done"]),
        ]

    @api.model
    def _scheduler_website_expire_cart(self, autocommit=False):
        websites = self.search([("cart_expire_delay", ">", 0)])
        if not websites:
            return True
        carts = self.env["sale.order"].search(
            expression.OR(
                [website._get_cart_expire_delay_domain() for website in websites]
            )
        )
        now = fields.Datetime.now()
        for cart in carts:
            if not cart.cart_expire_date or cart.cart_expire_date > now:
                continue
            try:
                with self.env.cr.savepoint():
                    cart.message_post(body=_("Cart expired"))
                    cart.action_cancel()
            except Exception as e:
                _logger.exception("Unable to cancel expired cart %s: %s", cart, e)
            else:
                if autocommit:
                    self.env.cr.commit()  # pylint: disable=invalid-commit
        return True
