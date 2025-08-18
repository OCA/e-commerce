# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    saleor_order_id = fields.Char(copy=False, index=True)
    saleor_channel_id = fields.Many2one("saleor.channel", string="Saleor Channel")
    saleor_delivery_carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Delivery Carrier",
    )
    saleor_mark_as_paid = fields.Boolean(copy=False, default=False)
    # --- Saleor order/payment info (populated by webhook) ---
    saleor_status = fields.Char(copy=False)
    saleor_number = fields.Char(copy=False)
    saleor_payment_id = fields.Char(copy=False)
    saleor_payment_gateway = fields.Char(copy=False)
    saleor_payment_charge_status = fields.Char(copy=False)
    saleor_payment_total = fields.Monetary(currency_field="currency_id", copy=False)
    saleor_payment_captured_amount = fields.Monetary(
        currency_field="currency_id", copy=False
    )
    saleor_payment_currency = fields.Char(copy=False)
    saleor_payment_psp_reference = fields.Char(copy=False)
    saleor_payment_updated = fields.Datetime(copy=False)
    saleor_payment_payload = fields.Text(copy=False)
    is_abandoned = fields.Boolean(default=False, readonly=True)

    def _saleor_prepare_address(self, partner):
        if not partner:
            return None
        country_area = None
        try:
            if partner.state_id:
                country_area = partner.state_id.code or partner.state_id.name or None
        except Exception:
            country_area = None
        return {
            "firstName": partner.name or "",
            "lastName": "",
            "streetAddress1": partner.street or "",
            "streetAddress2": partner.street2 or "",
            "city": partner.city or "",
            "postalCode": partner.zip or "",
            "country": (partner.country_id and partner.country_id.code) or None,
            "countryArea": country_area,
            "phone": partner.phone or partner.mobile or "",
        }

    def _saleor_prepare_order_payload(self):
        self.ensure_one()
        if not self.saleor_channel_id or not self.saleor_channel_id.saleor_channel_id:
            raise UserError(
                self.env._("Please select a Saleor Channel with remote ID.")
            )
        partner = self.partner_id
        billing = self._saleor_prepare_address(self.partner_invoice_id or partner)
        shipping = self._saleor_prepare_address(self.partner_shipping_id or partner)

        # Validate required state/region for certain countries
        def _needs_state(addr):
            return (addr or {}).get("country") in {"US", "CA"}

        for label, addr in (("Billing", billing), ("Shipping", shipping)):
            if _needs_state(addr) and not (addr or {}).get("countryArea"):
                raise UserError(
                    self.env._(
                        "%s address requires a State/Province for country %s.",
                        label,
                        (addr or {}).get("country") or "",
                    )
                )
        user_id = getattr(partner, "saleor_customer_id", None)
        payload = {
            "channelId": self.saleor_channel_id.saleor_channel_id,
            "billingAddress": billing,
            "shippingAddress": shipping,
            "lines": [
                {
                    "variantId": line.product_id.saleor_variant_id,
                    "quantity": int(line.product_uom_qty),
                }
                for line in self.order_line
                if line.product_id
                and line.product_id.saleor_variant_id
                and line.display_type is False
                and not getattr(line, "is_delivery", False)
            ],
        }
        # Optional fields: include only if present
        if user_id:
            payload["user"] = user_id
        elif partner.email:
            payload["userEmail"] = partner.email
        missing = [
            line.product_id.display_name
            for line in self.order_line
            if line.product_id
            and not line.product_id.saleor_variant_id
            and line.display_type is False
            and not getattr(line, "is_delivery", False)
        ]
        if missing:
            raise UserError(
                self.env._(
                    "The following products are not synced"
                    " to Saleor (no variant ID): %s",
                    ", ".join(sorted(set(missing))),
                )
            )
        return payload

    def action_sync_to_saleor(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(self) == 1:
            payload = self._saleor_prepare_order_payload()
            account.job_order_sync(self.id, payload)
            return True
        # Multiple: batch
        batch_size = getattr(account, "job_batch_size", 10) or 10
        items = []
        for order in self:
            payload = order._saleor_prepare_order_payload()
            items.append({"id": order.id, "payload": payload})
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            if hasattr(account, "with_delay"):
                account.with_delay().job_order_sync_batch(chunk)
            else:
                account.job_order_sync_batch(chunk)
        return True

    def action_mark_paid_in_saleor(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        for order in self:
            if not order.saleor_order_id:
                raise UserError(
                    self.env._("This order is not linked to a Saleor order.")
                )
            client = account._get_client()
            account._refresh_token(client)
            tx_ref = f"Odoo-{order.name}" if order.name else None
            res = client.order_mark_as_paid(
                order.saleor_order_id, transaction_reference=tx_ref
            )
            try:
                order.message_post(
                    body=self.env._(
                        "Marked as paid in Saleor (order: %s)",
                        (res or {}).get("id") or order.saleor_order_id,
                    )
                )
                order.write({"saleor_mark_as_paid": True})
            except Exception as e:
                _logger.warning(
                    "Failed to post 'Marked as paid' message on sale.order %s: %s",
                    order.id,
                    e,
                )
        return True
