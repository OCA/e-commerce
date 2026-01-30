from odoo import fields, models

from ..utils import _logger


class SaleorWebhookActivation(models.Model):
    _name = "saleor.webhook.activation"
    _description = "Saleor Webhook Activation"

    name = fields.Char(required=True)
    status = fields.Selection(
        selection=[("inactive", "Inactive"), ("active", "Active")],
        default="inactive",
        required=True,
    )
    saleor_account_id = fields.Many2one(
        comodel_name="saleor.account",
        string="Saleor Account",
        required=True,
        ondelete="cascade",
    )

    def _sync_status_to_saleor(self):
        for rec in self:
            account = rec.saleor_account_id
            if not account or not account.saleor_app_id:
                continue
            client = account._get_client()
            is_active = rec.status == "active"
            name = (rec.name or "").strip().lower()
            field_name = None
            if name == "customer":
                field_name = "saleor_customer_webhook_id"
            elif name == "payment":
                field_name = "saleor_payment_webhook_id"
            elif name == "order":
                field_name = "saleor_order_webhook_id"
            elif name == "draft order":
                field_name = "saleor_draft_order_webhook_id"
            if not field_name:
                continue
            webhook_id = getattr(account, field_name, None)
            if not webhook_id:
                continue
            try:
                client.webhook_update(webhook_id=webhook_id, is_active=is_active)
            except Exception as e:  # pragma: no cover - best-effort sync
                _logger.warning(
                    "Failed to sync Saleor webhook activation for account %s (%s): %s",
                    account.id,
                    rec.name,
                    e,
                )

    def write(self, vals):
        res = super().write(vals)
        if "status" in vals:
            self._sync_status_to_saleor()
        return res
