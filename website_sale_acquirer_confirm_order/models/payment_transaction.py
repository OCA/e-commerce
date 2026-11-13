# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _post_process(self):
        # Confirm the orders when the pending transaction is post-processed, so
        # they are confirmed even if the customer never reaches the confirmation page
        # (skip link, closed tab), as the post-processing cron also covers them.
        res = super()._post_process()
        txs = self.filtered(
            lambda tx: tx.state == "pending"
            and tx.operation != "validation"
            and tx.provider_id.confirm_order
        )
        txs.sale_order_ids.filtered(
            lambda so: so.state in ("draft", "sent")
        ).action_confirm()
        return res
