# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    cart_expire_date = fields.Datetime(
        compute="_compute_cart_expire_date",
        help="Technical field: The date this cart will automatically expire",
    )

    def _should_bypass_cart_expiration(self):
        """Hook method to prevent a cart from expiring"""
        self.ensure_one()
        # We don't want to cancel carts that are already in payment.
        return any(
            tx.state in ["pending", "authorized", "done"] for tx in self.transaction_ids
        )

    @api.depends(
        "write_date",
        "website_id.cart_expire_delay",
        "transaction_ids.last_state_change",
    )
    def _compute_cart_expire_date(self):
        for rec in self:
            if (
                rec.state == "draft"
                and rec.website_id.cart_expire_delay
                and not rec._should_bypass_cart_expiration()
            ):
                # In case of draft records, use current date
                from_date = rec.write_date or fields.Datetime.now()
                # In case or records with transactions, consider last tx date
                if rec.transaction_ids:
                    last_tx_date = max(rec.transaction_ids.mapped("last_state_change"))
                    from_date = max(from_date, last_tx_date)
                expire_delta = timedelta(hours=rec.website_id.cart_expire_delay)
                rec.cart_expire_date = from_date + expire_delta
            elif rec.cart_expire_date:
                rec.cart_expire_date = False
