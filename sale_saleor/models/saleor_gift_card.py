# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account


class SaleorGiftCard(models.Model):
    _name = "saleor.giftcard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Saleor Gift Card"

    name = fields.Char(readonly=True, copy=False)
    amount = fields.Float(
        required=True,
        default=1,
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        help="Currency allowed must belong to any Saleor channel.",
    )
    available_currency_ids = fields.Many2many(
        "res.currency",
        compute="_compute_available_currencies",
    )
    tag_ids = fields.Many2many("saleor.giftcard.tag", string="Tags")
    send_to_customer = fields.Boolean(string="Send gift card to customer")
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        help="Selected customer will be sent the generated gift card code."
        " Someone else can redeem the gift card code."
        "Gift card will be assigned to account which redeemed the code.",
    )
    channel_id = fields.Many2one(
        "saleor.channel",
        string="Channel",
        help="Customer will be sent the gift card code via this channels email address",
    )
    set_expiry_date = fields.Boolean(string="Set gift card expiry date")
    expiry_type = fields.Selection(
        selection=[
            ("duration", "Expires in"),
            ("exact", "Exact date"),
        ],
        default="duration",
    )
    expiry_duration = fields.Integer(
        string="Duration",
        help="Number of months until expiry",
        default=12,
    )
    expiry_unit = fields.Selection(
        selection=[
            ("years", "Years After Issue"),
            ("months", "Months After Issue"),
            ("weeks", "Weeks After Issue"),
            ("days", "Days After Issue"),
        ],
        default="months",
        required=True,
    )
    expiry_date = fields.Date(
        string="Exact expiry date",
        default=fields.Date.context_today,
    )
    note = fields.Text(
        help="Why was this gift card issued."
        " This note will not be shown to the customer."
        " Note will be stored in gift card history.",
    )
    requires_activation = fields.Boolean(
        string="Requires activation",
        default=True,
        help="Gift card must be activated by staff before use",
    )
    status = fields.Selection(
        selection=[
            ("disabled", "Disabled"),
            ("active", "Active"),
            ("expired", "Expired"),
        ],
        required=True,
        tracking=True,
        default="disabled",
    )
    code = fields.Char()
    saleor_giftcard_id = fields.Char(readonly=True, copy=False, index=True)
    saleor_metadata_line_ids = fields.One2many(
        "saleor.giftcard.meta.line",
        "giftcard_id",
        string="Meta Lines",
    )
    saleor_private_metadata_line_ids = fields.One2many(
        "saleor.giftcard.private.meta.line",
        "giftcard_id",
        string="Private Meta Lines",
    )

    @api.depends()
    def _compute_available_currencies(self):
        channels = self.env["saleor.channel"].search([])
        currencies = channels.mapped("currency_id").ids
        for rec in self:
            rec.available_currency_ids = [(6, 0, currencies)]

    @api.onchange("channel_id")
    def _onchange_channel_set_currency(self):
        for rec in self:
            if rec.channel_id and rec.channel_id.currency_id:
                rec.currency_id = rec.channel_id.currency_id

    def action_activate_giftcard(self):
        """Activate and sync gift cards to Saleor via account job."""
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        use_delay = len(self) > 1 and hasattr(account, "with_delay")
        for giftcard in self:
            giftcard.status = "active"
            if not giftcard.currency_id:
                raise UserError(_("Please set a currency before activation."))
            payload = giftcard._saleor_prepare_payload()
            if use_delay:
                account.with_delay().job_giftcard_activate(giftcard.id, payload)
            else:
                account.job_giftcard_activate(giftcard.id, payload)

    def action_deactivate_giftcard(self):
        for giftcard in self:
            giftcard.status = "disabled"

    @api.onchange("expiry_duration", "expiry_unit")
    def _onchange_compute_expiration_date(self):
        for rec in self:
            if rec.expiry_date and rec.expiry_type == "duration":
                today = fields.Date.context_today(self)
                duration = rec.expiry_duration or 0
                unit = rec.expiry_unit
                exp = None
                if duration > 0:
                    if unit == "days":
                        exp = today + timedelta(days=duration)
                    elif unit == "weeks":
                        exp = today + timedelta(weeks=duration)
                    elif unit == "months":
                        exp = today + relativedelta(months=+duration)
                    elif unit == "years":
                        exp = today + relativedelta(years=+duration)
                rec.expiry_date = exp

    def _saleor_prepare_payload(self):
        """Build GiftCardCreateInput payload for Saleor from this record."""
        self.ensure_one()
        balance = {
            "amount": float(self.amount or 0.0),
            "currency": self.currency_id.name,
        }
        user_email = (
            self.partner_id.email if self.send_to_customer and self.partner_id else None
        )
        channel_id = (
            getattr(self.channel_id, "saleor_channel_id", None)
            if self.send_to_customer
            else None
        )

        expiry_date = None
        if self.set_expiry_date:
            # Only use expiry_date field (no exact_date support)
            expiry_date = self.expiry_date

        payload = {
            "isActive": True,
            "balance": balance,
            "note": self.note or "",
        }
        # Saleor expects addTags in GiftCardCreateInput (not `tags`)
        tag_names = [t.name for t in self.tag_ids] if self.tag_ids else []
        if tag_names:
            payload["addTags"] = tag_names
        # Public metadata
        if self.saleor_metadata_line_ids:
            payload["metadata"] = [
                {"key": line.key, "value": line.value}
                for line in self.saleor_metadata_line_ids
                if line.key
            ]
        # Private metadata
        if self.saleor_private_metadata_line_ids:
            payload["privateMetadata"] = [
                {"key": line.key, "value": line.value}
                for line in self.saleor_private_metadata_line_ids
                if line.key
            ]
        if user_email:
            payload["userEmail"] = user_email
        if channel_id:
            payload["channel"] = channel_id
        if expiry_date:
            payload["expiryDate"] = fields.Date.to_string(expiry_date)
        return payload
