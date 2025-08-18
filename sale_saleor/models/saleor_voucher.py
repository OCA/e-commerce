# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..helpers import get_active_saleor_account, to_saleor_datetime


class SaleorVoucher(models.Model):
    _name = "saleor.voucher"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Saleor Voucher"

    name = fields.Char(required=True)
    channel_ids = fields.Many2many(
        "saleor.channel",
        "saleor_channel_voucher_rel",
        "channel_id",
        "voucher_id",
        string="Channels",
    )
    voucher_code_ids = fields.One2many(
        "saleor.voucher.code", "voucher_id", string="Voucher Codes"
    )
    type = fields.Selection(
        selection=[
            ("fixed", "Fixed Amount"),
            ("percent", "Percentage"),
            ("shipping", "Free Shipping"),
        ],
        required=True,
        default="fixed",
    )
    country_ids = fields.Many2many(
        "res.country",
        "saleor_voucher_country_rel",
        "voucher_id",
        "country_id",
        string="Assigned Countries",
    )
    apply_to = fields.Selection(
        selection=[
            ("all", "All products"),
            ("specific", "Specific products and variants"),
        ],
        default="all",
        required=True,
    )
    apply_cheapest = fields.Boolean(
        "Apply only to a single cheapest eligible product",
        help="If this option is disabled,"
        " discount will be counted for every eligible product",
        default=False,
    )
    # Minimum requirements
    min_requirement = fields.Selection(
        selection=[
            ("none", "None"),
            ("order_value", "Minimal order value"),
            ("item_qty", "Minimum quantity of items"),
        ],
        required=True,
        default="none",
    )
    min_item_qty = fields.Float("Minimum quantity of items")
    minimal_order_value_ids = fields.One2many(
        "saleor.voucher.minimal.order.value",
        "voucher_id",
    )
    # Usage Limit
    limit_total = fields.Boolean(
        "Limit number of times this discount can be used in total"
    )
    limit_uses = fields.Integer("Limit of Uses")
    uses_left = fields.Integer(string="Uses Left", related="limit_uses", readonly=True)
    limit_one_per_customer = fields.Boolean("Limit to one use per customer")
    limit_staff_only = fields.Boolean("Limit to staff only")
    limit_once_per_code = fields.Boolean("Limit voucher code use once")
    # Active Dates
    set_end_date = fields.Boolean()
    active_date_from = fields.Datetime(string="Start Date")
    active_date_to = fields.Datetime(string="End Date")
    saleor_voucher_metadata_line_ids = fields.One2many(
        "saleor.voucher.meta.line",
        "voucher_id",
    )
    saleor_voucher_private_metadata_line_ids = fields.One2many(
        "saleor.voucher.private.meta.line", "voucher_id"
    )
    discount_line_ids = fields.One2many(
        "saleor.voucher.discount.line",
        "voucher_id",
        string="Discount per Channel",
    )
    saleor_voucher_id = fields.Char(
        string="Saleor Voucher ID",
        copy=False,
        index=True,
        help="ID of this voucher in Saleor",
    )
    product_template_ids = fields.Many2many(
        "product.template",
        "saleor_voucher_product_template_rel",
        "voucher_id",
        "product_tmpl_id",
        string="Products",
    )
    product_variant_ids = fields.Many2many(
        "product.product",
        "saleor_voucher_product_variant_rel",
        "voucher_id",
        "product_id",
        string="Variants",
    )
    product_collection_ids = fields.Many2many(
        "product.collection",
        "saleor_voucher_product_collection_rel",
        "voucher_id",
        "collection_id",
        string="Collections",
    )
    product_category_ids = fields.Many2many(
        "product.category",
        "saleor_voucher_product_category_rel",
        "voucher_id",
        "category_id",
        string="Categories",
    )

    _sql_constraints = [
        (
            "check_min_item_qty_nonnegative",
            "CHECK(min_item_qty >= 0)",
            "Minimum quantity of items must be greater than or equal to 0.",
        ),
    ]

    @api.onchange("type")
    def _onchange_type_clear_discount_values(self):
        for rec in self:
            rec.discount_line_ids = [(5, 0, 0)]

    # --- Sync helpers ---
    def _map_saleor_types(self):
        """Return (saleor_type, saleor_value_type) based on voucher config."""
        self.ensure_one()
        # Value type
        if self.type == "fixed":
            saleor_value_type = "FIXED"
        elif self.type == "percent":
            saleor_value_type = "PERCENTAGE"
        else:
            saleor_value_type = None

        # Voucher type
        if self.apply_to == "specific":
            saleor_type = "SPECIFIC_PRODUCT"
        elif self.type == "shipping":
            saleor_type = "SHIPPING"
        else:
            saleor_type = "ENTIRE_ORDER"

        return saleor_type, saleor_value_type

    def _build_dates_payload(self):
        vals = {}
        if self.active_date_from:
            vals["startDate"] = to_saleor_datetime(self.active_date_from)
        if self.set_end_date and self.active_date_to:
            vals["endDate"] = to_saleor_datetime(self.active_date_to)
        return vals

    def _build_limits_payload(self):
        vals = {}
        if self.limit_total and self.limit_uses:
            vals["usageLimit"] = int(self.limit_uses)
        if self.limit_one_per_customer:
            vals["applyOncePerCustomer"] = True
        if self.apply_cheapest:
            vals["applyOncePerOrder"] = True
        if self.limit_once_per_code:
            vals["singleUse"] = True
        if self.limit_staff_only:
            vals["onlyForStaff"] = True
        return vals

    def _build_metadata_payload(self):
        vals = {}
        meta_lines = self.saleor_voucher_metadata_line_ids
        if meta_lines:
            vals["metadata"] = [
                {"key": line.key, "value": line.value}
                for line in meta_lines
                if line.key
            ]
        priv_lines = self.saleor_voucher_private_metadata_line_ids
        if priv_lines:
            vals["privateMetadata"] = [
                {"key": line.key, "value": line.value}
                for line in priv_lines
                if line.key
            ]
        return vals

    def _build_min_spent_map(self):
        min_spent_map = {}
        if self.min_requirement == "order_value" and self.minimal_order_value_ids:
            for mov in self.minimal_order_value_ids:
                ch = mov.channel_id
                if ch and ch.saleor_channel_id:
                    min_spent_map[ch.saleor_channel_id] = mov.minimal_order_value or 0.0
        return min_spent_map

    def _build_channel_listings(self, saleor_type, min_spent_map):
        channel_lines = []
        for dline in self.discount_line_ids:
            ch = dline.channel_id
            if ch and ch.saleor_channel_id:
                item = {"channelId": ch.saleor_channel_id}
                if saleor_type != "SHIPPING":
                    item["discountValue"] = dline.discount_value or 0.0
                if ch.saleor_channel_id in min_spent_map:
                    item["amount"] = min_spent_map[ch.saleor_channel_id]
                channel_lines.append(item)
        for channel_id, amount in min_spent_map.items():
            if not any(row.get("channelId") == channel_id for row in channel_lines):
                channel_lines.append({"channelId": channel_id, "amount": amount})
        return channel_lines

    def _build_requirements_payload(self):
        vals = {}
        if self.min_requirement == "item_qty" and self.min_item_qty:
            vals["minCheckoutItemsQuantity"] = int(self.min_item_qty)
        return vals

    def _collect_codes(self):
        return [code.code for code in self.voucher_code_ids if code.code]

    def _saleor_prepare_payload(self):
        self.ensure_one()
        # Types
        saleor_type, saleor_value_type = self._map_saleor_types()

        # Base
        payload = {"name": self.name, "type": saleor_type}
        if saleor_value_type:
            payload["discountValueType"] = saleor_value_type

        # Dates, limits, countries, metadata
        payload.update(self._build_dates_payload())
        payload.update(self._build_limits_payload())
        if self.country_ids:
            payload["countries"] = [country.code for country in self.country_ids]
        payload.update(self._build_metadata_payload())

        # Channels and requirements
        min_spent_map = self._build_min_spent_map()
        channel_lines = self._build_channel_listings(saleor_type, min_spent_map)
        if channel_lines:
            payload["channelListings"] = channel_lines
        payload.update(self._build_requirements_payload())

        # Codes
        codes = self._collect_codes()
        if codes:
            payload["codes"] = codes

        return payload

    def action_saleor_sync(self):
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if not account:
            return True
        if len(self) == 1:
            rec = self
            payload = rec._saleor_prepare_payload()
            account.job_voucher_sync(rec.id, payload)
        else:
            # Multiple: batch
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for rec in self:
                payload = rec._saleor_prepare_payload()
                items.append({"id": rec.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_voucher_sync_batch(chunk)
                else:
                    account.job_voucher_sync_batch(chunk)
        return True

    # Auto-activate all codes whenever the voucher is saved
    def _activate_codes(self):
        for rec in self:
            if rec.voucher_code_ids:
                rec.voucher_code_ids.write({"status": "active"})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._activate_codes()
        missing_start = records.filtered(lambda r: not r.active_date_from)
        if missing_start:
            missing_start.write({"active_date_from": fields.Datetime.now()})
        return records

    def write(self, vals):
        res = super().write(vals)
        self._activate_codes()
        return res

    @api.constrains("min_item_qty")
    def _check_min_item_qty_nonnegative(self):
        for rec in self:
            if rec.min_item_qty is not None and rec.min_item_qty < 0:
                raise ValidationError(
                    self.env._(
                        "Minimum quantity of items must be greater than or equal to 0."
                    )
                )
