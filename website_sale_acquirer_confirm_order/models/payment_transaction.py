# Copyright 2026 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _set_pending(self, state_message=None, **kwargs):
        # Confirm the orders as soon as the transaction is set pending, so they are
        # confirmed even if the customer never reaches the confirmation page
        # (skip link, closed tab): pending transactions are never post-processed.
        txs_to_process = super()._set_pending(state_message=state_message, **kwargs)
        txs = txs_to_process.filtered(
            lambda tx: tx.operation != "validation" and tx.provider_id.confirm_order
        )
        txs.sale_order_ids.filtered(
            lambda so: so.state in ("draft", "sent")
        ).action_confirm()
        return txs_to_process
