# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError

from ..controllers.main import CreditController


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "credit":
            return res
        return {
            "api_url": CreditController._process_url,
            "reference": self.reference,
        }

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "credit" or len(tx) == 1:
            return tx
        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "credit")]
        )
        if not tx:
            raise ValidationError(
                _("On Credit: No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != "credit":
            return
        self.sale_order_ids.action_confirm()
        self._set_pending(
            "Payment registered as credit: order confirmed, awaiting collection."
        )
