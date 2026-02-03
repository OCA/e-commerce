# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import secrets
import time
from datetime import timedelta
from functools import partial

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..helpers import (
    decode_image_field,
    format_batch_errors_message,
    format_kv_list,
    format_note,
    generate_unique_slug,
    make_link,
    post_to_current_job_committed,
    saleor_dashboard_links,
    upsert_tax_class,
)
from ..utils import SaleorClient, _logger


# --- Module-level helpers (reusable) ---
def saleor_collection_do_update(client, _id, payload, filename, file_bytes, ctype):
    """Update a collection with optional background image."""
    return client.collection_update(
        _id,
        payload,
        filename=filename,
        file_bytes=file_bytes,
        content_type=ctype,
    )


def saleor_product_do_update(client, _id, payload, filename, file_bytes, ctype):
    """Update a product (image upload handled separately)."""
    del filename, file_bytes, ctype  # not used for product update
    return client.product_update(_id, payload)


def saleor_attribute_do_update(client, _id, payload, filename, file_bytes, ctype):
    """Update an attribute; media params unused."""
    del filename, file_bytes, ctype
    return client.attribute_update(_id, payload)


class SaleorAccount(models.Model):
    _name = "saleor.account"
    _description = "Saleor Account"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    TOKEN_EXPIRY_MINUTES = 4
    DEFAULT_APP_PERMISSIONS = ["MANAGE_USERS", "MANAGE_TAXES", "MANAGE_ORDERS"]

    name = fields.Char(required=True)
    base_url = fields.Char(
        required=True, help="Base URL of the Saleor site", string="Saleor Base URL"
    )
    email = fields.Char(required=True, help="Saleor staff user email for API auth")
    password = fields.Char(
        required=True,
        groups="sale_saleor.group_saleor_manager",
    )
    odoo_base_url = fields.Char(
        string="Odoo Base URL", help="Enter the base URL of your Odoo instance"
    )

    customer_webhook_url = fields.Char(
        string="Webhook Target URL",
        compute="_compute_webhook_url",
        help="This URL is automatically generated",
        store=True,
    )
    payment_webhook_url = fields.Char(
        string="Payment Webhook URL",
        compute="_compute_webhook_url",
        help="Auto-generated URL for order payment updates",
        store=True,
    )
    order_webhook_url = fields.Char(
        string="Order Webhook URL",
        compute="_compute_webhook_url",
        help="Auto-generated URL for order created/updated",
        store=True,
    )
    draft_order_webhook_url = fields.Char(
        string="Draft Order Webhook URL",
        compute="_compute_webhook_url",
        help="Auto-generated URL for draft order created/updated",
        store=True,
    )

    verify_ssl = fields.Boolean(default=True)

    token = fields.Char(
        readonly=True,
        store=False,
        groups="sale_saleor.group_saleor_manager",
    )
    token_expiry = fields.Datetime(
        readonly=True,
        store=False,
        groups="sale_saleor.group_saleor_manager",
    )
    active = fields.Boolean(default=False)

    # Batch size for queue jobs when syncing multiple records
    job_batch_size = fields.Integer(default=10, string="Batch Size")

    # App/Webhook automation fields
    saleor_app_id = fields.Char(copy=False, readonly=True, string="Saleor App ID")
    saleor_app_token = fields.Char(
        copy=False,
        readonly=True,
        groups="sale_saleor.group_saleor_manager",
    )
    saleor_customer_webhook_id = fields.Char(
        copy=False, readonly=True, string="Saleor Webhook ID"
    )
    saleor_payment_webhook_id = fields.Char(
        copy=False, readonly=True, string="Saleor Payment Webhook ID"
    )
    saleor_webhook_secret = fields.Char(
        copy=False,
        help="HMAC secret used to verify incoming webhook payloads from Saleor",
        groups="sale_saleor.group_saleor_manager",
    )
    saleor_order_webhook_id = fields.Char(
        copy=False, readonly=True, string="Saleor Order Webhook ID"
    )
    saleor_draft_order_webhook_id = fields.Char(
        copy=False, readonly=True, string="Saleor Draft Order Webhook ID"
    )

    webhook_activation_ids = fields.One2many(
        comodel_name="saleor.webhook.activation",
        inverse_name="saleor_account_id",
        string="Webhook Activations",
    )

    def _get_client(self):
        self.ensure_one()
        # Prefer App token if available (long-lived). Otherwise use staff JWT.
        client = SaleorClient(self.base_url, verify_ssl=self.verify_ssl)
        if self.saleor_app_token:
            client.set_token(self.saleor_app_token)
        else:
            self._refresh_token(client)
        return client

    @api.depends("odoo_base_url")
    def _compute_webhook_url(self):
        """Compute webhook target URLs based on the Odoo base URL."""
        for rec in self:
            if rec.odoo_base_url:
                base = rec.odoo_base_url.rstrip("/")
                rec.customer_webhook_url = base + "/saleor/webhook/customer"
                rec.payment_webhook_url = base + "/saleor/webhook/order_payment"
                rec.order_webhook_url = base + "/saleor/webhook/order_created_updated"
                rec.draft_order_webhook_url = base + "/saleor/webhook/draft_order"
            else:
                rec.customer_webhook_url = False
                rec.payment_webhook_url = False
                rec.order_webhook_url = False
                rec.draft_order_webhook_url = False

    @api.constrains("active")
    def _check_single_active_account(self):
        for rec in self:
            if rec.active:
                count_active = self.search_count([("active", "=", True)])
                if count_active > 1:
                    raise UserError(
                        _("Only one Saleor account can be active at a time.")
                    )

    def _refresh_token(self, client=None):
        self.ensure_one()
        client = client or SaleorClient(self.base_url, verify_ssl=self.verify_ssl)

        # Fast-path: in-memory cache on the current record
        now = fields.Datetime.now()
        if self.token and self.token_expiry and now < self.token_expiry:
            client.set_token(self.token)
            return self.token

        # Acquire a row-level lock to prevent concurrent refreshes.
        self.env.cr.execute(
            "SELECT id FROM saleor_account WHERE id = %s FOR UPDATE NOWAIT",
            (self.id,),
        )

        # Re-read after lock acquisition to see if another worker already refreshed
        fresh = self.sudo().browse(self.id)
        now = fields.Datetime.now()
        if fresh.token and fresh.token_expiry and now < fresh.token_expiry:
            client.set_token(fresh.token)
            # Update in-memory cache on current record
            self.token = fresh.token
            self.token_expiry = fresh.token_expiry
            return fresh.token

        # Token actually expired or missing; perform a real refresh
        token = client.token_create(self.email, self.password)
        expiry = now + timedelta(minutes=self.TOKEN_EXPIRY_MINUTES)
        fresh.write({"token": token, "token_expiry": expiry})
        client.set_token(token)
        # Update in-memory cache for the current record
        self.token = token
        self.token_expiry = expiry
        return token

    # --- App/Webhook automation ---
    def _ensure_app_and_webhook(self):
        """Ensure a Saleor App exists with proper permissions and a webhook
        pointing to our computed webhook_url. Store the app token for future API calls.
        """
        self.ensure_one()
        if not self.active or not self.customer_webhook_url:
            return

        # Use staff JWT to create/ensure the App; then store app token for future use
        staff_client = SaleorClient(self.base_url, verify_ssl=self.verify_ssl)
        # Authenticate staff client to allow app create/update
        try:
            self._refresh_token(staff_client)
        except Exception as e:
            _logger.warning("Failed to authenticate staff client for app ensure: %s", e)
        app_id, app_token = self._ensure_app(staff_client)
        vals = {}
        if app_id and self.saleor_app_id != app_id:
            vals["saleor_app_id"] = app_id
        if app_token and self.saleor_app_token != app_token:
            vals["saleor_app_token"] = app_token
        if vals:
            self.write(vals)

        # Ensure we have a secret
        if not self.saleor_webhook_secret:
            self.saleor_webhook_secret = secrets.token_hex(32)

        # Ensure customer and payment webhooks
        client = SaleorClient(
            self.base_url,
            verify_ssl=self.verify_ssl,
            token=self.saleor_app_token or None,
        )
        self._ensure_webhook(
            client,
            self.customer_webhook_url,
            "saleor_customer_webhook_id",
            ["CUSTOMER_UPDATED"],
            "Customer",
        )
        self._ensure_webhook(
            client,
            self.payment_webhook_url,
            "saleor_payment_webhook_id",
            ["ORDER_PAID", "ORDER_FULLY_PAID"],
            "Payment",
        )
        self._ensure_webhook(
            client,
            self.order_webhook_url,
            "saleor_order_webhook_id",
            ["ORDER_CREATED", "ORDER_UPDATED"],
            "Order",
        )
        self._ensure_webhook(
            client,
            self.draft_order_webhook_url,
            "saleor_draft_order_webhook_id",
            ["DRAFT_ORDER_CREATED", "DRAFT_ORDER_UPDATED"],
            "Draft Order",
        )

    def _ensure_app(self, staff_client):
        """Ensure a Saleor App exists and has required permissions."""
        # Basic idempotency: try find existing App by stored ID
        app = None
        if self.saleor_app_id:
            try:
                app = staff_client.app_get_by_id(self.saleor_app_id)
            except Exception as e:
                _logger.warning(
                    "Failed to fetch Saleor App %s by id: %s",
                    self.saleor_app_id,
                    e,
                )
                app = None
        if not app:
            permissions = self.DEFAULT_APP_PERMISSIONS
            app_name = f"Odoo Integration ({self.name})"
            res = staff_client.app_create(
                name=app_name, permissions=permissions, is_active=True
            )
            return (res and res.get("id"), res and res.get("authToken"))
        # Update permissions best-effort
        try:
            staff_client.app_update(
                app.get("id"), permissions=self.DEFAULT_APP_PERMISSIONS
            )
        except Exception as e:
            _logger.warning("Failed to update Saleor App %s: %s", app.get("id"), e)
        return (app.get("id"), None)

    def _ensure_webhook(self, client, url, id_field, events, name_suffix):
        """Generic helper to ensure a Saleor webhook exists and is up to date."""

        target_url = url
        if not target_url:
            _logger.debug(
                "Saleor %s webhook ensure skipped"
                " because target URL is empty on account %s",
                name_suffix,
                self.name,
            )
            return

        webhook_id = getattr(self, id_field, None)
        webhook = None
        try:
            if webhook_id:
                webhook = client.webhook_get_by_id(webhook_id)
        except Exception as e:
            _logger.warning(
                "Failed to fetch existing Saleor %s webhook %s for account %s: %s",
                name_suffix,
                webhook_id,
                self.name,
                e,
            )
            webhook = None

        if webhook:
            need_update = webhook.get("targetUrl") != target_url
            if need_update:
                upd = client.webhook_update(
                    webhook_id=webhook.get("id"),
                    target_url=target_url,
                    events=events,
                    secret_key=self.saleor_webhook_secret,
                )
                if upd and upd.get("id") and upd.get("id") != webhook_id:
                    self.write({id_field: upd.get("id")})
                if upd:
                    webhook = upd
        else:
            created = client.webhook_create(
                app_id=self.saleor_app_id,
                target_url=target_url,
                events=events,
                secret_key=self.saleor_webhook_secret,
                is_active=True,
                name=f"Odoo {name_suffix} Webhook ({self.name})",
            )
            if created and created.get("id"):
                self.write({id_field: created.get("id")})

        webhook_obj = created or webhook or {}
        activation_name = webhook_obj.get("name") or name_suffix
        Activation = self.env["saleor.webhook.activation"].sudo()
        existing = Activation.search(
            [
                ("saleor_account_id", "=", self.id),
                ("name", "=", activation_name),
            ],
            limit=1,
        )
        if existing:
            if activation_name and existing.name != activation_name:
                existing.write({"name": activation_name})
        else:
            Activation.create(
                {
                    "name": activation_name,
                    "status": "inactive",
                    "saleor_account_id": self.id,
                }
            )

    # --- Saleor → Odoo Order upsert ---
    def _import_saleor_order(self, order):
        """Idempotently create/update a sale.order from a Saleor order payload."""
        self.ensure_one()
        if not order:
            return False

        unit_uom = self._get_default_unit_uom()
        saleor_order_id = order.get("id")
        number = order.get("number")
        status = order.get("status")

        partner, inv_partner, ship_partner = self._resolve_partner_and_addresses(order)
        channel_rec = self._resolve_channel(order)

        so = self._find_or_create_sale_order(
            saleor_order_id,
            number,
            status,
            partner,
            inv_partner,
            ship_partner,
            channel_rec,
        )

        self._compute_discount_total(order)
        # Only modify order lines and shipping while the order is in draft/sent
        if so.state in ("draft", "sent"):
            # Rebuild lines safely in draft
            so.order_line.unlink()
            self._add_order_lines(so, order, unit_uom)
            self._add_shipping_line(so, order, saleor_order_id)
        else:
            pass
        # If the Saleor order is no longer in DRAFT status, ensure the quotation
        # is not considered abandoned anymore.
        if status and status != "DRAFT" and hasattr(so, "is_abandoned"):
            so.write({"is_abandoned": False})
        self._store_payment_info(so, order)
        self._post_sync_message(so, number, saleor_order_id)

        return so.id

    def _get_default_unit_uom(self):
        try:
            return self.env.ref("uom.product_uom_unit", raise_if_not_found=False)
        except Exception:
            return False

    def _resolve_partner_and_addresses(self, order):
        Partner = self.env["res.partner"].sudo()
        user = order.get("user") or {}
        customer_id = user.get("id") or None
        email = user.get("email") or None
        first = user.get("firstName") or ""
        last = user.get("lastName") or ""
        cust_name = (first + " " + last).strip() or email or "Saleor Customer"

        # Prefer matching by Saleor IDs when provided
        partner = None
        if customer_id:
            partner = Partner.search(
                [
                    ("saleor_customer_id", "=", customer_id),
                    ("saleor_account_id", "=", self.id),
                ],
                limit=1,
            )
            # If not found by IDs, try by email to adopt identifiers
            if not partner and email:
                partner = Partner.search([("email", "=ilike", email)], limit=1)
                if partner:
                    partner.write(
                        {
                            "saleor_customer_id": customer_id,
                            "saleor_account_id": self.id,
                        }
                    )

        # If still not found, or no customer_id provided, fall back to email-only
        if not partner and email:
            partner = Partner.search([("email", "=ilike", email)], limit=1)

        # Create partner if needed
        if not partner:
            vals = {"name": cust_name, "email": email or False}
            if customer_id:
                vals.update(
                    {
                        "saleor_customer_id": customer_id,
                        "saleor_account_id": self.id,
                    }
                )
            partner = Partner.create(vals)

        # Ensure basic fields (name/email) are up to date
        to_write = {}
        if cust_name and partner.name != cust_name:
            to_write["name"] = cust_name
        if email and (partner.email or "").lower() != (email or "").lower():
            to_write["email"] = email
        if customer_id:
            # Persist identifiers if missing
            if not getattr(partner, "saleor_customer_id", None):
                to_write["saleor_customer_id"] = customer_id
            if not getattr(partner, "saleor_account_id", None):
                to_write["saleor_account_id"] = self.id
        if to_write:
            partner.write(to_write)

        # Child addresses
        billing = order.get("billingAddress") or {}
        shipping = order.get("shippingAddress") or {}
        inv_partner = self._ensure_child_partner(partner, billing, "invoice")
        ship_partner = self._ensure_child_partner(partner, shipping, "delivery")
        return partner, inv_partner, ship_partner

    def _ensure_child_partner(self, parent, addr, atype):
        Partner = self.env["res.partner"].sudo()
        if not addr:
            return parent
        vals = {
            "parent_id": parent.id,
            "type": atype,
            "name": (addr.get("firstName") or "") + " " + (addr.get("lastName") or ""),
            "street": addr.get("streetAddress1") or "",
            "street2": addr.get("streetAddress2") or "",
            "city": addr.get("city") or "",
            "zip": addr.get("postalCode") or "",
            "phone": addr.get("phone") or "",
        }
        country_code = (
            (addr.get("country") or {}).get("code") if addr.get("country") else None
        )
        if country_code:
            country = (
                self.env["res.country"]
                .sudo()
                .search([("code", "=", country_code)], limit=1)
            )
            if country:
                vals["country_id"] = country.id
                state_code = addr.get("countryArea") or None
                if state_code:
                    state = (
                        self.env["res.country.state"]
                        .sudo()
                        .search(
                            [
                                ("code", "=", state_code),
                                ("country_id", "=", country.id),
                            ],
                            limit=1,
                        )
                    )
                    if state:
                        vals["state_id"] = state.id
        child = Partner.search(
            [
                ("parent_id", "=", parent.id),
                ("type", "=", atype),
                ("street", "=", vals["street"]),
                ("zip", "=", vals["zip"]),
            ],
            limit=1,
        )
        if child:
            child.write(vals)
        else:
            child = Partner.create(vals)
        return child

    def _resolve_channel(self, order):
        ch = order.get("channel") or {}
        ch_id = ch.get("id")
        ch_slug = ch.get("slug")
        Channel = self.env["saleor.channel"].sudo()
        channel_rec = None
        if ch_id:
            channel_rec = Channel.search([("saleor_channel_id", "=", ch_id)], limit=1)
        if not channel_rec and ch_slug:
            channel_rec = Channel.search([("slug", "=", ch_slug)], limit=1)
        return channel_rec

    def _find_or_create_sale_order(
        self,
        saleor_order_id,
        number,
        status,
        partner,
        inv_partner,
        ship_partner,
        channel_rec,
    ):
        SaleOrder = self.env["sale.order"].sudo()
        so = SaleOrder.search([("saleor_order_id", "=", saleor_order_id)], limit=1)
        # Base values always safe to set
        base_vals = {
            "saleor_order_id": saleor_order_id,
            "saleor_number": number,
            "saleor_status": status,
        }
        if channel_rec:
            base_vals["saleor_channel_id"] = channel_rec.id
        if so:
            if so.state in ("draft", "sent"):
                partner_vals = {
                    "partner_id": partner.id,
                    "partner_invoice_id": inv_partner.id if inv_partner else partner.id,
                    "partner_shipping_id": ship_partner.id
                    if ship_partner
                    else partner.id,
                }
                so.write({**partner_vals, **base_vals})
            else:
                so.write(base_vals)
        else:
            create_vals = {
                "partner_id": partner.id,
                "partner_invoice_id": inv_partner.id if inv_partner else partner.id,
                "partner_shipping_id": ship_partner.id if ship_partner else partner.id,
                **base_vals,
            }
            so = SaleOrder.create(create_vals)
        return so

    def _compute_discount_total(self, order):
        total = 0.0
        for d in order.get("discounts") or []:
            amt = ((d or {}).get("amount") or {}).get("amount")
            try:
                total += float(amt or 0)
            except Exception as e:
                _logger.debug("Failed to parse discount amount '%s': %s", amt, e)
        return total

    def _add_order_lines(self, so, order, unit_uom):
        ProductProduct = self.env["product.product"].sudo()
        ProductTemplate = self.env["product.template"].sudo()
        for line in order.get("lines") or []:
            qty = int((line or {}).get("quantity") or 0)
            if qty <= 0:
                continue
            var = (line or {}).get("variant") or {}
            var_id = var.get("id")
            prod = None
            if var_id:
                prod = ProductProduct.search(
                    [("saleor_variant_id", "=", var_id)], limit=1
                )
            if not prod:
                pname = (line or {}).get(
                    "productName"
                ) or f"Saleor Variant {var_id or ''}"
                tvals2 = {"name": pname, "type": "product"}
                if unit_uom:
                    tvals2.update({"uom_id": unit_uom.id, "uom_po_id": unit_uom.id})
                tmpl = ProductTemplate.create(tvals2)
                prod = ProductProduct.create(
                    {"product_tmpl_id": tmpl.id, "saleor_variant_id": var_id or False}
                )
            up = (line or {}).get("unitPrice") or {}
            net_amt = (up.get("net") or {}).get("amount")
            try:
                unit_price = float(net_amt or 0.0)
            except Exception:
                unit_price = 0.0
            self.env["sale.order.line"].sudo().create(
                {
                    "order_id": so.id,
                    "product_id": prod.id,
                    "product_uom_qty": qty,
                    "price_unit": unit_price,
                }
            )

    def _add_shipping_line(self, so, order, saleor_order_id):
        sp = order.get("shippingPrice") or {}
        net_sp = (sp.get("net") or {}).get("amount")
        try:
            ship_total = float(net_sp or 0.0)
        except Exception:
            ship_total = 0.0
        if not ship_total:
            return
        ship_prod = None
        sm = None
        sm_name = None
        try:
            sm_node = order.get("shippingMethod") or {}
            sm = sm_node.get("id")
            sm_name = sm_node.get("name")
            carrier = None
            if sm_name:
                carrier = (
                    self.env["delivery.carrier"]
                    .sudo()
                    .search(
                        [("delivery_type", "=", "saleor"), ("name", "=", sm_name)],
                        limit=1,
                    )
                )
                if not carrier:
                    carrier = (
                        self.env["delivery.carrier"]
                        .sudo()
                        .search(
                            [
                                ("delivery_type", "=", "saleor"),
                                ("name", "ilike", sm_name),
                            ],
                            limit=1,
                        )
                    )
            if not carrier and sm:
                carrier = (
                    self.env["delivery.carrier"]
                    .sudo()
                    .search(
                        [("saleor_shipping_method_id", "=", sm)],
                        limit=1,
                    )
                )
            if carrier:
                try:
                    so.sudo().write({"carrier_id": carrier.id})
                except Exception:
                    _logger.debug("Could not set carrier_id on sale.order %s", so.id)
            if carrier and carrier.product_id:
                ship_prod = carrier.product_id
        except Exception:
            ship_prod = None
        if ship_prod:
            self.env["sale.order.line"].sudo().create(
                {
                    "order_id": so.id,
                    "product_id": ship_prod.id,
                    "product_uom_qty": 1,
                    "price_unit": ship_total,
                }
            )
        else:
            _logger.warning(
                "Saleor order %s: shipping method %s not mapped"
                " to a carrier product; skipping shipping line",
                saleor_order_id,
                sm or "(none)",
            )

    def _store_payment_info(self, so, order):
        pays = order.get("payments") or []
        if not pays:
            return
        p = pays[0] or {}
        total_money = p.get("total") or {}
        cap_money = p.get("capturedAmount") or {}
        try:
            total_amt = float(total_money.get("amount") or 0.0)
        except Exception:
            total_amt = 0.0
        try:
            cap_amt = float(cap_money.get("amount") or 0.0)
        except Exception:
            cap_amt = 0.0
        curr = total_money.get("currency") or cap_money.get("currency")
        vals = {
            "saleor_payment_id": p.get("id"),
            "saleor_payment_gateway": p.get("gateway"),
            "saleor_payment_charge_status": p.get("chargeStatus"),
            "saleor_payment_total": total_amt,
            "saleor_payment_captured_amount": cap_amt,
            "saleor_payment_currency": curr,
            "saleor_payment_psp_reference": p.get("pspReference"),
        }
        so.write(vals)

    def _post_sync_message(self, so, number, saleor_order_id):
        try:
            dash_url, obj_url = saleor_dashboard_links(
                self.base_url, "order", id=saleor_order_id, number=number
            )
            body = format_kv_list(
                "Synced from Saleor:",
                [
                    ("Account", self.email or self.name),
                    ("Order", number or saleor_order_id),
                    ("Saleor", make_link("View in Saleor", obj_url)),
                ],
            )
            so.message_post(body=body)
        except Exception as e:
            _logger.debug(
                "Failed to post Saleor sync message on order %s: %s", so.id, e
            )

    # Hooks to auto-ensure app/webhook
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # Run after creation if active set
        for rec in res:
            if rec.active and (rec.customer_webhook_url or rec.payment_webhook_url):
                rec._ensure_app_and_webhook()
        return res

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            # If active turned on or webhook URL(s) changed, ensure webhook/app
            if rec.active and (
                "active" in vals
                or "odoo_base_url" in vals
                or "webhook_url" in vals
                or "payment_webhook_url" in vals
            ):
                rec._ensure_app_and_webhook()
        return res

    def _sync_parent_and_set_payload_parent(self, odoo_cat, payload):
        parent = odoo_cat.parent_id
        if not parent:
            return
        if not payload.get("parent"):
            if not parent.saleor_category_id:
                parent_payload = parent._saleor_prepare_payload()
                # Sync parent directly in same account context
                self.job_category_sync(parent.id, parent_payload)
            if parent.saleor_category_id:
                payload["parent"] = parent.saleor_category_id

    def _ensure_slug_and_get_existing(self, client, odoo_cat, payload):
        slug = payload.get("slug")
        if not slug:
            name = payload.get("name") or odoo_cat.name
            if name:
                slug = generate_unique_slug(
                    odoo_cat,
                    name,
                    slug_field_name="saleor_slug",
                )
                if slug:
                    payload["slug"] = slug
        if slug:
            self._refresh_token(client)
            existing = client.category_get_by_slug(slug)
        else:
            existing = None
        return slug, existing

    def _prepare_image(self, rec, extra_images=False):
        """Prepare image bytes for supported records.

        - Category: field saleor_background_image
        - Collection: field saleor_background_image
        - Product: field saleor_image_ids
        """
        img_bytes = None
        filename = None
        content_type = "application/octet-stream"

        # Category/Collection background image
        if getattr(rec, "saleor_background_image", False):
            img_bytes, filename, content_type = decode_image_field(
                rec.saleor_background_image, base_filename="collection"
            )
            return (img_bytes, filename, content_type) if not extra_images else []

        # Product images
        if rec._name == "product.template" and hasattr(rec, "saleor_image_ids"):
            if not extra_images:
                return None, None, None

            images = []
            for img in rec.saleor_image_ids.sorted("sequence"):
                # Skip if image already has a Saleor ID
                if img.saleor_image_id:
                    continue

                if img.image_1920:
                    img_data = decode_image_field(
                        img.image_1920, base_filename=f"product-{img.id}"
                    )
                    if img_data[0]:  # If image data is valid
                        images.append(
                            (
                                img_data[0],
                                img_data[1],
                                img_data[2],
                                img.name or "",
                                img.sequence or 0,
                                img,
                            )
                        )

            if extra_images:
                return images

        return None, None, None

    def _raise_if_updating_parent(self, odoo_cat, payload):
        if payload.get("parent") and odoo_cat.saleor_category_id:
            raise UserError(
                _(
                    "Saleor does not support updating a category's parent. "
                    "Please change the parent directly in Saleor"
                    " or create a new category."
                )
            )

    def _post_image_success(self, odoo_cat, slug, payload, saleor_id, img_bytes):
        # Optionally post image upload note if image present
        if saleor_id and img_bytes:
            try:
                odoo_cat.message_post(
                    body=format_note(
                        self.env,
                        "Uploaded category background image to Saleor (account %s)",
                        self.email,
                    )
                )
            except Exception as e:
                _logger.warning(
                    "Failed to post background image upload message on category %s: %s",
                    odoo_cat.id,
                    e,
                )
        try:
            dash_url, obj_url = saleor_dashboard_links(
                self.base_url,
                "category",
                id=saleor_id,
                slug=slug or payload.get("slug") or payload.get("name"),
            )
            body = format_kv_list(
                "Synced to Saleor:",
                [
                    ("Account", self.email),
                    ("Slug", slug or payload.get("slug") or payload.get("name")),
                    ("Saleor ID", saleor_id),
                    ("Saleor", make_link("View in Saleor", obj_url)),
                ],
            )
            odoo_cat.message_post(body=body)
        except Exception as e:
            _logger.warning("Failed to post sync message on category: %s", e)

    def _sync_promotion_rules(self, client, program, saleor_promotion_id):
        """Upsert rules for a promotion based on Odoo Discount Rules.

        - Create missing rules (by stored ID or matching name).
        - Update existing rules' basic data (name, description).
        Note: Conditions/rewards mapping can be added later when schema is finalized.
        """
        rules = program.discount_rule_ids
        if not rules:
            _logger.debug(
                "Saleor promotion sync: no discount rules found for program %s [%s]",
                getattr(program, "name", ""),
                getattr(program, "id", ""),
            )
            return True

        # Fetch existing rules from Saleor to resolve names when ID missing
        remote_rules = client.promotion_rules_list(saleor_promotion_id) or []
        remote_by_id = {r.get("id"): r for r in remote_rules if r.get("id")}
        remote_by_name = {r.get("name"): r for r in remote_rules if r.get("name")}

        for rule in rules:
            input_data = rule._saleor_prepare_rule_input()
            saleor_rule_id = rule.saleor_promotion_rule_id
            # Collect desired channels from rule
            rule_channels = []
            try:
                ch = getattr(rule, "channel_id", False)
                if ch and getattr(ch, "saleor_channel_id", None):
                    rule_channels = [ch.saleor_channel_id]
            except Exception:
                rule_channels = []
            # Try by stored ID
            if saleor_rule_id and saleor_rule_id in remote_by_id:
                if rule_channels:
                    client.promotion_rule_update(
                        saleor_rule_id, input_data, add_channels=rule_channels
                    )
                else:
                    client.promotion_rule_update(saleor_rule_id, input_data)
                continue
            # Else try matching by name
            if input_data.get("name") and input_data["name"] in remote_by_name:
                found = remote_by_name[input_data["name"]]
                fr_id = found.get("id")
                if fr_id:
                    if rule_channels:
                        client.promotion_rule_update(
                            fr_id, input_data, add_channels=rule_channels
                        )
                    else:
                        client.promotion_rule_update(fr_id, input_data)
                    if not saleor_rule_id:
                        rule.write({"saleor_promotion_rule_id": fr_id})
                    continue
            # No match -> create
            created = client.promotion_rule_create(
                saleor_promotion_id, input_data, channels=rule_channels or None
            )
            cr_id = (created or {}).get("id")
            if cr_id and not saleor_rule_id:
                rule.write({"saleor_promotion_rule_id": cr_id})
        return True

    # Job: sync a product.category to this Saleor
    #  account (create if missing by slug else update)
    def job_category_sync(self, category_id, payload):
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor category sync skipped for category %s on inactive account %s",
                category_id,
                self.name,
            )
            return True
        client = self._get_client()
        odoo_cat = self.env["product.category"].browse(category_id)
        # Ensure parent synced and inject parent id
        self._sync_parent_and_set_payload_parent(odoo_cat, payload)

        # Ensure slug and check existing
        slug, existing = self._ensure_slug_and_get_existing(client, odoo_cat, payload)

        # Prepare optional image payload
        img_bytes, filename, content_type = self._prepare_image(odoo_cat)

        saleor_id = None
        if existing and existing.get("id"):
            self._raise_if_updating_parent(odoo_cat, payload)
            if "parent" in payload:
                payload = dict(payload)
                payload.pop("parent", None)
            self._refresh_token(client)
            cat = client.category_update(
                existing["id"],
                payload,
                filename=filename,
                file_bytes=img_bytes,
                content_type=content_type,
            )
            saleor_id = (cat or {}).get("id") or existing.get("id")
        else:
            self._refresh_token(client)
            cat = client.category_create(
                payload,
                filename=filename,
                file_bytes=img_bytes,
                content_type=content_type,
            )
            saleor_id = (cat or {}).get("id")
        # Persist and post messages
        self._persist_saleor_id(odoo_cat, "category", saleor_id)
        self._post_image_success(odoo_cat, slug, payload, saleor_id, img_bytes)
        return True

    # --- Batch jobs ---
    def job_category_sync_batch(self, items):
        """Batch sync categories."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor category batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            cat_id = it.get("id")
            payload = it.get("payload")
            try:
                self.job_category_sync(cat_id, payload)
            except Exception as e:
                rec = self.env["product.category"].browse(cat_id)
                rec_name = rec.display_name if rec else f"category[{cat_id}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch category sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            raise UserError(header)
        return True

    def _resync_template_variants(self, tmpl):
        """Resync all variants of a product.template to Saleor."""
        self.ensure_one()
        if not tmpl or not tmpl.exists() or not tmpl.saleor_product_id:
            return True

        variants = tmpl.product_variant_ids
        if not variants:
            return True

        by_sku, by_saleor_id = self._variant_build_local_indexes(variants)

        client = self._get_client()
        remote_variants = self._variant_fetch_remote(client, tmpl)
        if remote_variants is False:
            # Remote fetch failed; abort quietly
            return False

        remote_ids, to_delete_ids = self._variant_compute_deletions(
            remote_variants, by_sku, by_saleor_id
        )

        self._variant_remove_obsolete(client, tmpl, to_delete_ids)
        self._variant_clear_stale_ids(variants, remote_ids, to_delete_ids)

        items = self._variant_build_sync_items(variants, tmpl.saleor_product_id)
        if not items:
            return True

        self._variant_enqueue_sync_batches(items, tmpl)

        # After variants resync, ensure product channel listings still match
        # Odoo template channels.
        self._variant_resync_product_channels(tmpl)

        return True

    def _variant_build_local_indexes(self, variants):
        by_sku = {
            v.default_code: v for v in variants if getattr(v, "default_code", False)
        }
        by_saleor_id = {
            v.saleor_variant_id: v
            for v in variants
            if getattr(v, "saleor_variant_id", False)
        }
        return by_sku, by_saleor_id

    def _variant_fetch_remote(self, client, tmpl):
        try:
            self._refresh_token(client)
            return (
                client.product_variants_list_by_product_id(tmpl.saleor_product_id) or []
            )
        except Exception as e:
            _logger.warning(
                "Failed to fetch remote variants for product %s: %s",
                tmpl.display_name,
                e,
            )
            return False

    def _variant_compute_deletions(self, remote_variants, by_sku, by_saleor_id):
        remote_ids = set()
        to_delete_ids = []
        for rv in remote_variants:
            rv = rv or {}
            rid = rv.get("id")
            sku = rv.get("sku")
            if rid:
                remote_ids.add(rid)
            if rid and (rid not in by_saleor_id) and (not sku or sku not in by_sku):
                to_delete_ids.append(rid)
        return remote_ids, to_delete_ids

    def _variant_remove_obsolete(self, client, tmpl, to_delete_ids):
        if not to_delete_ids:
            return
        try:
            self._refresh_token(client)
            client.product_variant_bulk_delete(to_delete_ids)
        except Exception as e:
            _logger.warning(
                "Failed to bulk delete obsolete variants for product %s: %s",
                tmpl.display_name,
                e,
            )

    def _variant_clear_stale_ids(self, variants, remote_ids, to_delete_ids):
        valid_remote_ids = remote_ids.difference(to_delete_ids)
        for v in variants:
            sid = getattr(v, "saleor_variant_id", False)
            if sid and sid not in valid_remote_ids:
                try:
                    v.write({"saleor_variant_id": False})
                except Exception as e:
                    _logger.warning(
                        "Failed to clear stale Saleor Variant ID on %s: %s",
                        v.display_name,
                        e,
                    )

    def _variant_build_sync_items(self, variants, saleor_product_id):
        items = []
        for v in variants:
            try:
                payload = v._saleor_prepare_variant_payload(saleor_product_id)
            except Exception as e:
                _logger.warning(
                    "Failed to build payload for variant %s: %s",
                    v.display_name,
                    e,
                )
                continue
            items.append(
                {
                    "variant_id": v.id,
                    "product_saleor_id": saleor_product_id,
                    "payload": payload,
                }
            )
        return items

    def _variant_enqueue_sync_batches(self, items, tmpl):
        batch_size = getattr(self, "job_batch_size", 10) or 10
        for i in range(0, len(items), batch_size):
            chunk = items[i : i + batch_size]
            try:
                if hasattr(self, "with_delay"):
                    self.with_delay().job_product_variant_sync_batch(chunk)
                else:
                    self.job_product_variant_sync_batch(chunk)
            except Exception as e:
                _logger.warning(
                    "Failed to enqueue variant batch sync for product %s: %s",
                    tmpl.display_name,
                    e,
                )

    def _variant_resync_product_channels(self, tmpl):
        # After variants resync, ensure product channel listings still match
        # Odoo template channels.
        try:
            client = self._get_client()
            self._refresh_token(client)
            self._sync_product_channel_listings(client, tmpl, tmpl.saleor_product_id)
        except Exception as e:
            _logger.warning(
                "Failed to resync product channel listings for %s: %s",
                tmpl.display_name,
                e,
            )

    def job_product_variants_resync(self, product_tmpl_id):
        """Public job to resync all variants for a given product.template.

        This is typically invoked when attribute_line_ids change, to ensure
        Saleor variants match the current Odoo matrix.
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor variants resync skipped for template %s on inactive account %s",
                product_tmpl_id,
                self.name,
            )
            return True

        tmpl = self.env["product.template"].browse(product_tmpl_id)
        if not tmpl or not tmpl.exists() or not tmpl.saleor_product_id:
            return True

        return self._resync_template_variants(tmpl)

    def job_warehouse_sync(self, warehouse_id, payload):
        """Sync a single stock.warehouse to Saleor Warehouse.
        Name rule is prepared by warehouse: name + (short_name).
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor warehouse sync skipped for warehouse %s on inactive account %s",
                warehouse_id,
                self.name,
            )
            return True

        wh = self.env["stock.warehouse"].browse(warehouse_id)
        if not wh:
            _logger.debug(
                "Saleor warehouse sync skipped: warehouse %s not found on account %s",
                warehouse_id,
                self.name,
            )
            return True

        client = self._get_client()
        try:
            saleor_id = wh.saleor_warehouse_id
            # Map Odoo selection to Saleor boolean
            is_private_val = getattr(wh, "is_private", False)
            is_private_bool = True if is_private_val in ("private", True) else False
            if saleor_id:
                # Verify the remote warehouse exists; if not, re-create
                self._refresh_token(client)
                existing = client.warehouse_get_by_id(saleor_id)
                if not existing:
                    saleor_id = None
            if saleor_id:
                self._refresh_token(client)
                update_payload = dict(payload or {})
                update_payload["isPrivate"] = is_private_bool
                res = client.warehouse_update(saleor_id, update_payload)
                saleor_id = (res or {}).get("id") or saleor_id
            else:
                self._refresh_token(client)
                res = client.warehouse_create(payload)
                saleor_id = (res or {}).get("id")

                # After create, immediately update isPrivate (not accepted on create)
                if saleor_id is not None:
                    try:
                        self._refresh_token(client)
                        client.warehouse_update(
                            saleor_id,
                            {"isPrivate": is_private_bool},
                        )
                    except Exception as e2:
                        _logger.warning(
                            "Failed to set isPrivate on newly"
                            " created Saleor warehouse %s: %s",
                            saleor_id,
                            e2,
                        )

            if saleor_id and wh.saleor_warehouse_id != saleor_id:
                try:
                    wh.write({"saleor_warehouse_id": saleor_id})
                except Exception as e:
                    _logger.warning(
                        "Failed to persist Saleor Warehouse ID on warehouse %s: %s",
                        wh.id,
                        e,
                    )
            return bool(saleor_id)
        except Exception as e:
            _logger.exception(
                "Error syncing warehouse '%s' to Saleor via account %s: %s",
                wh.display_name,
                self.name,
                e,
            )
            emsg = str(e)
            if "postalCode" in emsg and "INVALID" in emsg:
                raise UserError(
                    _(
                        "Address validation failed: "
                        "The postal code is invalid for the selected country.\n"
                        "Please verify the ZIP/Postal Code format for your country"
                        " and update the partner's address."
                    )
                ) from e
            if "countryArea" in emsg and "INVALID" in emsg:
                raise UserError(
                    _(
                        "Address validation failed: "
                        "The state/region (country area) is invalid"
                        " for the selected country.\n"
                        "Please ensure it matches a valid subdivision name/code"
                        " for your country and update the partner's address."
                    )
                ) from e
            raise UserError(_("Saleor warehouse sync failed: %s", emsg)) from e

    def job_warehouse_sync_batch(self, items):
        """Batch sync warehouses."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor warehouse batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            wid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_warehouse_sync(wid, payload)
            except Exception as e:
                rec = self.env["stock.warehouse"].browse(wid)
                rec_name = rec.display_name if rec else f"warehouse[{wid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch warehouse sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def job_order_fulfill(self, sale_order_id):
        """Fulfill newly delivered quantities for a Saleor-linked order.

        This job supports both full and partial fulfillments by comparing
        each line's delivered quantity in Odoo with the quantity already
        fulfilled in Saleor (tracked via saleor_fulfilled_qty).
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor order fulfill skipped for order %s on inactive account %s",
                sale_order_id,
                self.name,
            )
            return True

        order = self.env["sale.order"].browse(sale_order_id)
        if not order or not order.exists():
            return True
        if not order.saleor_order_id:
            return True

        client = self._get_client()

        try:
            # Fetch remote order to obtain line IDs and variants
            self._refresh_token(client)
            remote_order = client.order_get_by_id(order.saleor_order_id) or {}
        except Exception as e:
            _logger.exception(
                "Error fetching Saleor order %s for fulfill via account %s: %s",
                order.saleor_order_id,
                self.name,
                e,
            )
            raise UserError(
                _("Saleor order fulfill failed while reading order: %s", e)
            ) from e

        remote_lines = (remote_order or {}).get("lines") or []
        by_id, by_variant = self._job_order_fulfill_build_remote_maps(remote_lines)

        default_saleor_wh = self._job_order_fulfill_default_warehouse()

        lines_payload, updates = self._job_order_fulfill_build_payload(
            order, by_id, by_variant, default_saleor_wh
        )

        if not lines_payload:
            _logger.debug(
                "Saleor order fulfill: no new quantities to fulfill for order %s",
                order.id,
            )
            return True

        try:
            self._refresh_token(client)
            res = client.order_fulfill(
                order.saleor_order_id,
                lines_payload,
                notify_customer=False,
                allow_stock_to_be_exceeded=True,
            )
            _logger.info(
                "Triggered Saleor fulfill for order %s via account %s: %s",
                order.saleor_order_id,
                self.name,
                res,
            )
        except Exception as e:
            _logger.exception(
                "Error calling orderFulfill for Saleor order %s via account %s: %s",
                order.saleor_order_id,
                self.name,
                e,
            )
            raise UserError(_("Saleor order fulfill failed: %s", str(e))) from e

        # Update local tracking of fulfilled quantities
        self._job_order_fulfill_update_local(updates)

        try:
            order.message_post(
                body=_(
                    "Pushed fulfillment to Saleor for %s line(s).",
                    len(lines_payload),
                )
            )
        except Exception as e:
            _logger.debug(
                "Failed to post Saleor fulfill message on sale.order %s: %s",
                order.id,
                e,
            )

        return True

    def _job_order_fulfill_build_remote_maps(self, remote_lines):
        by_id = {ln.get("id"): ln for ln in remote_lines if ln.get("id")}
        by_variant = {}
        for ln in remote_lines:
            var = (ln or {}).get("variant") or {}
            vid = var.get("id")
            if not vid:
                continue
            by_variant.setdefault(vid, []).append(ln)
        return by_id, by_variant

    def _job_order_fulfill_default_warehouse(self):
        saleor_wh_ids = set()
        try:
            Warehouses = (
                self.env["stock.warehouse"]
                .sudo()
                .search(
                    [
                        ("is_saleor_warehouse", "=", True),
                        ("include_in_saleor_inventory", "=", True),
                        ("saleor_warehouse_id", "!=", False),
                    ]
                )
            )
            Locations = (
                self.env["stock.location"]
                .sudo()
                .search(
                    [
                        ("is_saleor_warehouse", "=", True),
                        ("include_in_saleor_inventory", "=", True),
                        ("saleor_warehouse_id", "!=", False),
                    ]
                )
            )
            for wh in Warehouses:
                if wh.saleor_warehouse_id:
                    saleor_wh_ids.add(wh.saleor_warehouse_id)
            for loc in Locations:
                if loc.saleor_warehouse_id:
                    saleor_wh_ids.add(loc.saleor_warehouse_id)
        except Exception as e:
            _logger.debug(
                "Failed to collect Saleor warehouses for fulfill: %s",
                e,
            )
        return next(iter(saleor_wh_ids), None)

    def _job_order_fulfill_build_payload(
        self, order, by_id, by_variant, default_saleor_wh
    ):
        lines_payload = []
        updates = []
        for line in order.order_line:
            if getattr(line, "display_type", False):
                continue
            if getattr(line, "is_delivery", False):
                continue
            product = getattr(line, "product_id", False)
            if not product:
                continue
            saleor_variant_id = getattr(product, "saleor_variant_id", None)
            if not saleor_variant_id:
                continue

            delivered = getattr(line, "qty_delivered", 0.0) or 0.0
            already = getattr(line, "saleor_fulfilled_qty", 0.0) or 0.0
            delta = delivered - already
            if delta <= 0:
                continue

            saleor_line_id = getattr(line, "saleor_order_line_id", None)
            if saleor_line_id and saleor_line_id in by_id:
                pass
            else:
                candidates = by_variant.get(saleor_variant_id) or []
                if candidates:
                    remote_ln = candidates[0]
                    saleor_line_id = remote_ln.get("id")
                    if saleor_line_id and not getattr(
                        line, "saleor_order_line_id", None
                    ):
                        try:
                            line.write({"saleor_order_line_id": saleor_line_id})
                        except Exception as e:
                            _logger.debug(
                                "Failed to store Saleor order line ID on line %s: %s",
                                line.id,
                                e,
                            )

            if not saleor_line_id:
                continue

            try:
                qty_int = int(delta)
            except Exception:
                qty_int = 0
            if qty_int <= 0 or not default_saleor_wh:
                continue

            lines_payload.append(
                {
                    "orderLineId": saleor_line_id,
                    "stocks": [{"warehouse": default_saleor_wh, "quantity": qty_int}],
                }
            )
            updates.append((line, qty_int))
        return lines_payload, updates

    def _job_order_fulfill_update_local(self, updates):
        for line, qty_int in updates:
            try:
                current = getattr(line, "saleor_fulfilled_qty", 0.0) or 0.0
                line.saleor_fulfilled_qty = current + float(qty_int)
            except Exception as e:
                _logger.debug(
                    "Failed to update saleor_fulfilled_qty on line %s: %s",
                    line.id,
                    e,
                )

    def job_location_sync(self, location_id, payload):
        """Sync a single stock.location to Saleor Warehouse.
        Name rule is complete_name of location.
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor location sync skipped for location %s"
                " on inactive account %s",
                location_id,
                self.name,
            )
            return True

        loc = self.env["stock.location"].browse(location_id)
        if not loc:
            return True

        client = self._get_client()
        try:
            saleor_id = loc.saleor_warehouse_id
            if saleor_id:
                # Verify the remote warehouse exists; if not, re-create
                self._refresh_token(client)
                existing = client.warehouse_get_by_id(saleor_id)
                if not existing:
                    saleor_id = None
            if saleor_id:
                self._refresh_token(client)
                res = client.warehouse_update(saleor_id, payload)
                saleor_id = (res or {}).get("id") or saleor_id
            else:
                self._refresh_token(client)
                res = client.warehouse_create(payload)
                saleor_id = (res or {}).get("id")

            if saleor_id and loc.saleor_warehouse_id != saleor_id:
                try:
                    loc.write({"saleor_warehouse_id": saleor_id})
                except Exception as e:
                    _logger.warning(
                        "Failed to persist Saleor Warehouse ID on location %s: %s",
                        loc.id,
                        e,
                    )
            return bool(saleor_id)
        except Exception as e:
            _logger.exception(
                "Error syncing location '%s' to Saleor via account %s: %s",
                loc.display_name,
                self.name,
                e,
            )
            # Raise a friendly error for the user instead of posting to chatter
            emsg = str(e)
            if "postalCode" in emsg and "INVALID" in emsg:
                raise UserError(
                    _(
                        "Address validation failed:"
                        " The postal code is invalid for the selected country.\n"
                        "Please verify the ZIP/Postal Code format for your country"
                        " and update the partner's address."
                    )
                ) from e
            if "countryArea" in emsg and "INVALID" in emsg:
                raise UserError(
                    _(
                        "Address validation failed:"
                        " The state/region (country area) is invalid for"
                        " the selected country.\n"
                        "Please ensure it matches a valid subdivision name/code"
                        " for your country and update the partner's address."
                    )
                ) from e
            raise UserError(_("Saleor location sync failed: %s", emsg)) from e

    def job_location_sync_batch(self, items):
        """Batch sync locations."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor location batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            lid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_location_sync(lid, payload)
            except Exception as e:
                rec = self.env["stock.location"].browse(lid)
                rec_name = rec.display_name if rec else f"location[{lid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch location sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            raise UserError(header)
        return True

    def job_product_variant_sync(  # noqa: C901
        self, variant_id, product_saleor_id, payload
    ):
        """Sync a single product.product variant to Saleor."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor variant sync skipped for variant %s"
                " (product %s) on inactive account %s",
                variant_id,
                product_saleor_id,
                self.name,
            )
            return True

        variant = self.env["product.product"].browse(variant_id)
        if not variant:
            return True

        client = self._get_client()
        self._refresh_token(client)

        try:
            # Upsert variant (update or create)
            saleor_id = self._variant_upsert(
                client, variant, product_saleor_id, payload
            )

            # Build and push channel listings if available
            if saleor_id:
                try:
                    update_channels = self._variant_build_channel_listings(
                        variant, payload
                    )
                    self._variant_push_channel_listings(
                        client, saleor_id, update_channels, variant
                    )
                except Exception as e:
                    _logger.warning(
                        "Failed to update variant channel listings for %s: %s",
                        variant.default_code or variant.id,
                        e,
                    )

                # Ensure initial stock rows exist in Saleor for enabled sources
                try:
                    # Collect Saleor-enabled warehouses and locations
                    Warehouses = (
                        self.env["stock.warehouse"]
                        .sudo()
                        .search(
                            [
                                ("is_saleor_warehouse", "=", True),
                                ("include_in_saleor_inventory", "=", True),
                                ("saleor_warehouse_id", "!=", False),
                            ]
                        )
                    )
                    Locations = (
                        self.env["stock.location"]
                        .sudo()
                        .search(
                            [
                                ("is_saleor_warehouse", "=", True),
                                ("include_in_saleor_inventory", "=", True),
                                ("saleor_warehouse_id", "!=", False),
                            ]
                        )
                    )
                    # De-duplicate by remote warehouse id
                    saleor_wh_ids = set()
                    for wh in Warehouses:
                        if wh.saleor_warehouse_id:
                            saleor_wh_ids.add(wh.saleor_warehouse_id)
                    for loc in Locations:
                        if loc.saleor_warehouse_id:
                            saleor_wh_ids.add(loc.saleor_warehouse_id)

                    if saleor_wh_ids:
                        for remote_wh_id in saleor_wh_ids:
                            try:
                                # Create stock entry with zero quantity idempotently
                                client.product_variant_stocks_create(
                                    variant_id=saleor_id,
                                    warehouse_id=remote_wh_id,
                                    quantity=0,
                                )
                            except Exception as se:
                                _logger.warning(
                                    "Failed to ensure initial stock for variant %s"
                                    " in Saleor warehouse %s: %s",
                                    saleor_id,
                                    remote_wh_id,
                                    se,
                                )
                except Exception as e:
                    _logger.debug(
                        "Skipping initial stock creation for variant %s due to: %s",
                        saleor_id,
                        e,
                    )

            # Post chatter success
            try:
                slug = (
                    (payload or {}).get("sku")
                    or variant.default_code
                    or str(variant.id)
                )
                self._post_success(
                    rec=variant,
                    object_type="product_variant",
                    slug=slug,
                    payload=payload or {},
                    saleor_id=saleor_id,
                )
            except Exception as e:
                _logger.warning("Failed to post variant sync message: %s", e)

            return bool(saleor_id)

        except Exception as e:
            _logger.exception(
                "Error syncing variant '%s' to Saleor via account %s: %s",
                variant.display_name,
                self.name,
                e,
            )
            raise UserError(_("Saleor variant sync failed: %s", str(e))) from e

    def job_product_variant_sync_batch(self, items):
        """Batch sync product variants."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor variant batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            vid = it.get("variant_id")
            pid = it.get("product_saleor_id")
            payload = it.get("payload")
            try:
                self.job_product_variant_sync(vid, pid, payload)
            except Exception as e:
                rec = self.env["product.product"].browse(vid)
                rec_name = rec.display_name if rec else f"variant[{vid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch product variant sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            raise UserError(header)
        return True

    def _variant_allowed_update_payload(self, payload):
        allowed = {"name", "sku", "trackInventory", "weight"}
        return {k: v for k, v in (payload or {}).items() if k in allowed}

    def _variant_upsert(self, client, variant, product_saleor_id, payload):
        """Update existing variant or create a new one, return Saleor ID."""
        saleor_id = None
        if variant.saleor_variant_id:
            existing = client.product_variant_get_by_id(variant.saleor_variant_id)
            if existing and existing.get("id"):
                input_payload = self._variant_allowed_update_payload(payload)
                res = client.product_variant_update(
                    variant.saleor_variant_id, input_payload
                )
                saleor_id = (res or {}).get("id") or variant.saleor_variant_id

        if not saleor_id:
            # Ensure SKU is never None/False; allow empty string if not set.
            sku_val = (payload or {}).get("sku")
            if not sku_val:
                sku_val = getattr(variant, "default_code", "") or ""
            res = client.product_variant_create(
                product_id=product_saleor_id,
                sku=sku_val,
                name=(payload or {}).get("name") or variant.name,
                attributes=(payload or {}).get("attributes") or [],
                weight=(payload or {}).get("weight"),
            )
            saleor_id = (res or {}).get("id")
            if saleor_id and variant.saleor_variant_id != saleor_id:
                try:
                    variant.write({"saleor_variant_id": saleor_id})
                except Exception as e:
                    _logger.warning(
                        "Failed to persist Saleor Variant ID on variant %s: %s",
                        variant.id,
                        e,
                    )
        return saleor_id

    def _variant_build_channel_listings(self, variant, payload):  # noqa: C901
        """Build channel listing payloads using provided channelListings"""
        listings = (payload or {}).get("channelListings") or []
        update_channels = []
        if listings:
            for it in listings:
                ch_id = (it or {}).get("channelId")
                entry = {"channelId": ch_id}
                price_val = (it or {}).get("price")
                if price_val is not None:
                    try:
                        if isinstance(price_val, dict):
                            price_val = price_val.get("amount")
                        entry["price"] = str(float(price_val))
                    except Exception as e:
                        _logger.debug(
                            "Saleor: skip price conversion for variant %s: %s",
                            variant.display_name,
                            e,
                        )
                try:
                    if variant.standard_price is not None:
                        entry["costPrice"] = str(float(variant.standard_price))
                except Exception as e:
                    _logger.debug(
                        "Saleor: skip costPrice conversion for variant %s: %s",
                        variant.display_name,
                        e,
                    )
                if ch_id:
                    update_channels.append(entry)
            return update_channels

        # Fallback to addChannels
        add_channels = (payload or {}).get("addChannels") or []
        if add_channels:
            channels = self.env["saleor.channel"].search(
                [("saleor_channel_id", "in", add_channels)]
            )
            by_id = {c.saleor_channel_id: c for c in channels}
            for ch_id in add_channels:
                ch = by_id.get(ch_id)
                if not ch:
                    continue
                entry = {
                    "channelId": ch_id,
                    "price": str(float(variant.lst_price or 0.0)),
                }
                try:
                    if variant.standard_price is not None:
                        entry["costPrice"] = str(float(variant.standard_price))
                except Exception as e:
                    _logger.debug(
                        "Saleor: skip costPrice conversion for variant %s: %s",
                        variant.display_name,
                        e,
                    )
                update_channels.append(entry)
        return update_channels

    def _variant_push_channel_listings(
        self, client, saleor_id, update_channels, variant
    ):
        if update_channels:
            self._refresh_token(client)
            client.product_variant_channel_listing_update(saleor_id, update_channels)

    def job_variant_stock_update(self, variant_id, warehouse_id, quantity):
        """Update stock for a product variant to Saleor."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor stock update skipped for variant %s,"
                " warehouse %s on inactive account %s",
                variant_id,
                warehouse_id,
                self.name,
            )
            return True

        client = self._get_client()
        self._refresh_token(client)
        try:
            res = client.product_variant_stocks_update(
                variant_id=variant_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
            )
            _logger.info(
                "Updated Saleor stock: variant=%s, warehouse=%s, qty=%s",
                variant_id,
                warehouse_id,
                quantity,
            )
            return res
        except Exception as e:
            _logger.exception(
                "Error updating Saleor stock for variant %s via account %s: %s",
                variant_id,
                self.name,
                e,
            )
            raise UserError(_("Saleor stock update failed: %s", str(e))) from e

    def job_variant_stock_delete(self, variant_id=None, sku=None, warehouse_ids=None):
        """Delete stock entries for a product variant in one or more warehouses."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor stock delete skipped for variant %s on inactive account %s",
                variant_id or sku,
                self.name,
            )
            return True

        client = self._get_client()
        self._refresh_token(client)
        try:
            res = client.product_variant_stocks_delete(
                variant_id=variant_id, sku=sku, warehouse_ids=warehouse_ids
            )
            _logger.info(
                "Deleted Saleor stock: variant=%s, warehouses=%s",
                variant_id or sku,
                warehouse_ids,
            )
            return res
        except Exception as e:
            _logger.exception(
                "Error deleting Saleor stock for variant %s via account %s: %s",
                variant_id or sku,
                self.name,
                e,
            )
            raise UserError(_("Saleor stock delete failed: %s", str(e))) from e

    def job_order_sync(self, order_id, payload):
        """Create a draft order in Saleor and add lines.

        payload is expected to contain keys: channelId, userId (optional), userEmail,
        billingAddress, shippingAddress, lines (list of {variantId, quantity}).
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor order sync skipped for order %s on inactive account %s",
                order_id,
                self.name,
            )
            return True

        order = self.env["sale.order"].browse(order_id)
        if not order:
            return True

        client = self._get_client()
        try:
            base_input = {
                "channelId": payload.get("channelId"),
                "user": payload.get("user"),
                "userEmail": payload.get("userEmail"),
                "billingAddress": payload.get("billingAddress"),
                "shippingAddress": payload.get("shippingAddress"),
            }
            base_input = {k: v for k, v in base_input.items() if v}
            # Mark order as originating from Odoo to avoid webhook loop
            marker = [{"key": "odoo_origin", "value": "true"}]
            base_input["privateMetadata"] = marker
            base_input["metadata"] = marker
            lines = payload.get("lines") or []

            self._refresh_token(client)
            channel_id = base_input.get("channelId") or payload.get("channelId")
            if channel_id and lines:
                unavail = self._preflight_check_variants(client, channel_id, lines)
                if unavail:
                    msg = ", ".join(sorted(set(unavail)))
                    raise UserError(
                        _(
                            "Cannot sync order: variants unavailable in channel: %s",
                            msg,
                        )
                    )

            shipping_addr = base_input.get("shippingAddress") or payload.get(
                "shippingAddress"
            )
            self._preflight_check_country(client, channel_id, shipping_addr)

            saleor_order_id = self._draft_order_create_or_update(
                client, order, base_input, lines
            )

            self._apply_shipping_method_to_order(client, order, saleor_order_id)

            if order.state == "sale":
                self._complete_draft_order(client, saleor_order_id)

            if saleor_order_id and order.saleor_order_id != saleor_order_id:
                try:
                    order.write({"saleor_order_id": saleor_order_id})
                except Exception as e:
                    _logger.warning(
                        "Failed to persist Saleor Order ID" " on sale.order %s: %s",
                        order.id,
                        e,
                    )

            try:
                dash_url, obj_url = saleor_dashboard_links(
                    self.base_url, "order", id=saleor_order_id, number=None
                )
                order.message_post(
                    body=format_kv_list(
                        "Synced to Saleor:",
                        [
                            ("Account", self.email or self.name),
                            ("Saleor Order ID", saleor_order_id),
                            ("Saleor", make_link("View in Saleor", obj_url)),
                        ],
                    )
                )
            except Exception as e:
                _logger.warning("Failed to post order sync message: %s", e)

            return bool(saleor_order_id)
        except Exception as e:
            _logger.exception(
                "Error syncing sale.order '%s' to Saleor via account %s: %s",
                order.display_name,
                self.name,
                e,
            )
            raise UserError(_("Saleor order sync failed: %s", str(e))) from e

    def job_order_sync_batch(self, items):
        """Batch sync sale orders."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor order batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            oid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_order_sync(oid, payload)
            except Exception as e:
                rec = self.env["sale.order"].browse(oid)
                rec_name = rec.display_name if rec else f"order[{oid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch order sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def _preflight_check_variants(self, client, channel_id, lines):
        """
        Return list of display names or IDs of variants not available in the channel.
        """
        missing = []

        # Collect unique variant IDs from lines
        variant_ids = self._collect_variant_ids_from_lines(lines)

        if not variant_ids:
            return missing

        try:
            variant_map = self._fetch_variant_map(client, variant_ids)
        except Exception:
            # In case of a total failure, fall back to marking all as missing
            missing.extend(variant_ids)
            return missing

        # Evaluate availability per line using the batched data
        for ln in lines or []:
            vid = ln.get("variantId")
            if not vid:
                continue
            v = variant_map.get(vid) or {}
            if not v:
                # If variant not returned by API, treat as missing
                missing.append(vid)
                continue

            label = self._compute_variant_missing_label(v, channel_id, vid)
            if label:
                missing.append(label)
        return missing

    def _collect_variant_ids_from_lines(self, lines):
        variant_ids = []
        seen = set()
        for ln in lines or []:
            vid = ln.get("variantId")
            if not vid:
                continue
            if vid not in seen:
                seen.add(vid)
                variant_ids.append(vid)
        return variant_ids

    def _fetch_variant_map(self, client, variant_ids):
        query = """
        query ProductVariants($ids: [ID!], $first: Int!) {
          productVariants(first: $first, ids: $ids) {
            edges {
              node {
                id
                name
                product {
                  id
                  name
                  channelListings {
                    channel { id }
                    isPublished
                  }
                }
                stocks {
                  warehouse { id name }
                  quantity
                }
              }
            }
          }
        }
        """

        variant_map = {}
        self._refresh_token(client)
        data = (
            client.graphql(
                query,
                {"ids": variant_ids, "first": len(variant_ids)},
            )
            or {}
        )
        edges = ((data.get("productVariants") or {}).get("edges")) or []
        for edge in edges:
            node = (edge or {}).get("node") or {}
            vid = node.get("id")
            if vid:
                variant_map[vid] = node
        return variant_map

    def _compute_variant_missing_label(self, variant_node, channel_id, default_label):
        prod = variant_node.get("product") or {}
        pid = prod.get("id")

        # Channel listing check taken from product.channelListings
        listed = False
        published = False
        if pid:
            cls = prod.get("channelListings") or []
            for cl in cls:
                ch = cl.get("channel") or {}
                if ch.get("id") == channel_id:
                    listed = True
                    published = bool(cl.get("isPublished"))
                    break

        # Basic stock check
        stocks = variant_node.get("stocks") or []
        try:
            total_qty = sum(int(s.get("quantity") or 0) for s in stocks)
        except Exception:
            total_qty = 0

        if not listed and not published and total_qty <= 0:
            # No signal of availability; fall back to default label without reasons
            return default_label

        if not listed or not published or total_qty <= 0:
            name = (
                variant_node.get("name")
                or (prod.get("name") if prod else None)
                or default_label
            )
            reasons = []
            if not listed:
                reasons.append("not listed")
            if listed and not published:
                reasons.append("unpublished")
            if total_qty <= 0:
                reasons.append("no stock")
            return f"{name} ({', '.join(reasons)})"

        return None

    def _preflight_check_country(self, client, channel_id, shipping_addr):
        country_code = (shipping_addr or {}).get("country")
        if channel_id and country_code:
            try:
                query = """
                query ShippingZones($first: Int!) {
                  shippingZones(first: $first) {
                    edges {
                      node {
                        countries { code }
                        channels { id }
                      }
                    }
                  }
                }
                """
                zones_data = client.graphql(query, {"first": 100}) or {}
                edges = ((zones_data.get("shippingZones") or {}).get("edges")) or []
                allowed = set()
                for edge in edges:
                    node = edge.get("node") or {}
                    chans = node.get("channels") or []
                    if any((c or {}).get("id") == channel_id for c in chans):
                        for c in node.get("countries") or []:
                            code = (c or {}).get("code")
                            if code:
                                allowed.add(code)
                _logger.debug(
                    "Saleor preflight: channel %s"
                    " allows countries: %s (checking %s)",
                    channel_id,
                    ",".join(sorted(allowed)) or "<none>",
                    country_code,
                )
                if allowed and country_code not in allowed:
                    raise UserError(
                        _(
                            "Shipping country %s is not available for channel."
                            " Please check Saleor Shipping Zones"
                            " assigned to the channel.",
                            country_code,
                        )
                    )
            except UserError:
                raise
            except Exception as e:
                _logger.debug(
                    "Preflight shipping country check skipped due to error: %s", e
                )

    def _draft_order_create_or_update(self, client, order, base_input, lines):
        saleor_order_id = order.saleor_order_id
        existing = None
        if saleor_order_id:
            self._refresh_token(client)
            try:
                existing = client.order_get_by_id(saleor_order_id)
            except Exception:
                existing = None
            if not existing:
                saleor_order_id = None

        if saleor_order_id and existing and (existing.get("status") == "DRAFT"):
            self._refresh_token(client)
            update_input = dict(base_input)
            if "channelId" in update_input:
                update_input.pop("channelId")
            client.draft_order_update(saleor_order_id, update_input)
            try:
                for ln in existing.get("lines") or []:
                    lid = (ln or {}).get("id")
                    if lid:
                        self._refresh_token(client)
                        client.order_line_delete(lid)
            except Exception as e:
                _logger.debug("Saleor: failed deleting some lines before re-add: %s", e)
            if lines:
                self._refresh_token(client)
                client.draft_order_lines_create(saleor_order_id, lines)
            return saleor_order_id

        if saleor_order_id and existing:
            return saleor_order_id

        self._refresh_token(client)
        created = client.draft_order_create(base_input)
        saleor_order_id = (created or {}).get("id")
        if saleor_order_id and lines:
            self._refresh_token(client)
            client.draft_order_lines_create(saleor_order_id, lines)
        return saleor_order_id

    def _apply_shipping_method_to_order(self, client, order, saleor_order_id):
        try:
            carrier = getattr(order, "saleor_delivery_carrier_id", False)
            if saleor_order_id and carrier:
                self._refresh_token(client)
                available = (
                    client.order_available_shipping_methods(saleor_order_id) or []
                )
                target_id = None
                carrier_name = getattr(carrier, "name", None)
                for m in available:
                    if (m or {}).get("name") == carrier_name:
                        target_id = m.get("id")
                        break
                if not target_id and len(available) == 1:
                    target_id = (available[0] or {}).get("id")
                if target_id:
                    client.order_update_shipping(saleor_order_id, target_id)
                else:
                    avail_names = ", ".join(
                        [(m or {}).get("name") or "<unnamed>" for m in available]
                    )
                    raise Exception(
                        "No matching ShippingMethod found for carrier"
                        " '{carrier_name}'. Available: {avail_names}"
                    )
        except Exception as e:
            _logger.warning(
                "Failed to set delivery method for Saleor order"
                " %s from carrier %s: %s",
                saleor_order_id,
                getattr(carrier, "name", carrier) if "carrier" in locals() else None,
                e,
            )

    def _complete_draft_order(self, client, saleor_order_id):
        try:
            if saleor_order_id:
                self._refresh_token(client)
                client.draft_order_complete(saleor_order_id)
        except Exception as e:
            _logger.warning(
                "Failed to complete Saleor draft order %s: %s",
                saleor_order_id,
                e,
            )

    # --- Collections ---
    # Job: sync a product.collection to this Saleor account
    #  (create if missing by slug else update)
    def job_collection_sync(self, collection_id, payload):
        return self.job_saleor_sync("collection", collection_id, payload)

    def job_collection_sync_batch(self, items):
        """Batch sync product collections."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor collection batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            col_id = it.get("id")
            payload = it.get("payload")
            try:
                self.job_collection_sync(col_id, payload)
            except Exception as e:
                rec = self.env["product.collection"].browse(col_id)
                rec_name = rec.display_name if rec else f"collection[{col_id}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch collection sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    # --- Unified post-success ---
    def _post_success(
        self,
        rec,
        object_type,
        slug,
        payload,
        saleor_id,
        img_uploaded=False,
        img_bytes=None,
    ):
        """Post a unified success message and optional image upload note.

        object_type: 'collection' | 'product' | 'product_variant'
        For collections, pass img_bytes; for products, pass img_uploaded.
        """
        try:
            if object_type == "product_variant":
                try:
                    parent_pid = getattr(
                        getattr(rec, "product_tmpl_id", None), "saleor_product_id", None
                    )
                except Exception:
                    parent_pid = None
                dash_url, obj_url = saleor_dashboard_links(
                    self.base_url,
                    "product_variant",
                    id=saleor_id,
                    product_id=parent_pid,
                )
                body = format_kv_list(
                    "Synced variant to Saleor successfully:",
                    [
                        ("Account", self.email),
                        (
                            "SKU",
                            slug
                            or payload.get("sku")
                            or payload.get("name")
                            or str(rec.id),
                        ),
                        ("Variant ID", saleor_id),
                        ("Saleor", make_link("Open in Saleor", obj_url)),
                    ],
                )
                rec.message_post(body=body)
            else:
                # Determine kind for deep link
                kind_map = {
                    "collection": "collection",
                    "product": "product",
                    "product_variant": "product",
                }
                kind = kind_map.get(object_type)
                dash_url, obj_url = saleor_dashboard_links(
                    self.base_url,
                    kind or object_type,
                    id=saleor_id,
                    slug=slug or payload.get("slug") or payload.get("name"),
                )
                slug_val = slug or payload.get("slug") or payload.get("name")
                storefront_url = None
                if kind == "product" and slug_val:
                    base = "https://storefront-gcr.staging-kencove.com".rstrip("/")
                    storefront_url = f"{base}/products/detail/{slug_val}"
                # For products, show explicit Storefront/Saleor links.
                if kind == "product":
                    body = format_kv_list(
                        "Synced to Saleor successfully:",
                        [
                            ("Account", self.email),
                            ("Slug", slug_val),
                            ("Saleor ID", saleor_id),
                            (
                                "Storefront",
                                make_link(
                                    "View in Storefront",
                                    storefront_url or dash_url,
                                ),
                            ),
                            (
                                "Saleor",
                                make_link("View in Saleor", obj_url),
                            ),
                        ],
                    )
                else:
                    body = format_kv_list(
                        "Synced to Saleor successfully:",
                        [
                            ("Account", self.email),
                            ("Slug", slug_val),
                            ("Saleor ID", saleor_id),
                            ("Saleor", make_link("Open in Saleor", obj_url)),
                        ],
                    )
                rec.message_post(body=body)
        except Exception as e:
            _logger.warning("Failed to post sync message on %s: %s", object_type, e)
        # Image notes
        try:
            if object_type == "collection" and saleor_id and img_bytes:
                rec.message_post(
                    body=format_note(
                        self.env,
                        "Uploaded collection background image to Saleor (account %s)",
                        self.email,
                    )
                )
            if object_type == "product" and img_uploaded:
                rec.message_post(
                    body=format_note(
                        self.env,
                        "Uploaded product image to Saleor (account %s)",
                        self.email,
                    )
                )
        except Exception as e:
            _logger.warning("Failed to post image note on %s: %s", object_type, e)

    def job_product_sync(self, product_tmpl_id, payload):
        return self.job_saleor_sync("product", product_tmpl_id, payload)

    def job_product_sync_batch(self, items):
        """Batch sync product templates."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor product batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            pt_id = it.get("id")
            payload = it.get("payload")
            try:
                self.job_product_sync(pt_id, payload)
            except Exception as e:
                rec = self.env["product.template"].browse(pt_id)
                rec_name = rec.display_name if rec else f"product[{pt_id}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch product sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def job_voucher_sync(self, voucher_id, payload):
        """Sync a single saleor.voucher to Saleor (create/update),
            update channel listings, and add codes.

        Resolution:
        - If Odoo has saleor_voucher_id, try by ID. If missing, fall back to name.
        - If found by name, persist ID; otherwise create new.
        Posts a chatter message and returns True on success.
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor voucher sync skipped for voucher %s" " on inactive account %s",
                voucher_id,
                self.name,
            )
            return True

        rec = self.env["saleor.voucher"].browse(voucher_id)
        if not rec:
            return True

        client = self._get_client()

        base_input = dict(payload or {})
        channel_listings = base_input.pop("channelListings", [])
        codes = base_input.pop("codes", [])
        metadata = base_input.pop("metadata", [])
        private_metadata = base_input.pop("privateMetadata", [])

        saleor_id = rec.saleor_voucher_id
        try:
            saleor_id, existing = self._voucher_resolve_and_upsert(
                client, rec, base_input, codes
            )
            # Metadata
            self._voucher_sync_metadata(client, saleor_id, metadata, private_metadata)

            # Channels
            self._voucher_update_channels(client, saleor_id, channel_listings)

            # Catalogues
            self._voucher_attach_catalogues(client, saleor_id, rec)

            # Codes
            self._voucher_add_codes(client, saleor_id, codes, existing)

            try:
                self._post_success(
                    rec=rec,
                    object_type="voucher",
                    slug=rec.name,
                    payload=payload or {},
                    saleor_id=saleor_id,
                )
            except Exception as e:
                _logger.warning("Failed to post voucher sync message: %s", e)

            return bool(saleor_id)

        except Exception as e:
            _logger.exception(
                "Error syncing voucher '%s' to Saleor via account %s: %s",
                rec.display_name,
                self.name,
                e,
            )
            raise UserError(_("Saleor voucher sync failed: %s", str(e))) from e

    def job_voucher_sync_batch(self, items):
        """Batch sync vouchers."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor voucher batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            vid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_voucher_sync(vid, payload)
            except Exception as e:
                rec = self.env["saleor.voucher"].browse(vid)
                rec_name = rec.display_name if rec else f"voucher[{vid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch voucher sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def job_giftcard_activate(self, giftcard_id, input_payload):  # noqa: C901
        """Upsert (create/update) a gift card in Saleor, then sync metadata.

        Expects input_payload per GiftCardCreateInput/GiftCardUpdateInput.
        On success writes:
        - status = active
        - saleor_giftcard_id, saleor_giftcard_code, code, name
        - posts chatter message
        And updates public/private metadata from line models if any.
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor gift card activate job skipped for giftcard %s"
                " on inactive account %s",
                giftcard_id,
                self.name,
            )
            return True

        rec = self.env["saleor.giftcard"].browse(giftcard_id)
        if not rec:
            return True

        client = self._get_client()
        try:
            self._refresh_token(client)
            # Create or Update depending on existing Saleor ID
            if rec.saleor_giftcard_id:
                # GiftCardUpdateInput does not accept some create-only fields
                blocked = {"balance", "channel", "isActive", "note"}
                update_payload = {
                    k: v for k, v in (input_payload or {}).items() if k not in blocked
                }
                remote = (
                    client.gift_card_update(rec.saleor_giftcard_id, update_payload)
                    or {}
                )
            else:
                remote = client.gift_card_create(input_payload or {}) or {}
            remote_id = remote.get("id")
            saleor_code = remote.get("code")
            saleor_display = remote.get("displayCode")

            vals = {
                "status": "active",
                "saleor_giftcard_id": remote_id,
            }
            if saleor_code or saleor_display:
                if saleor_code:
                    vals["code"] = saleor_code
                if saleor_display:
                    vals["name"] = saleor_display
            if vals:
                try:
                    rec.write(vals)
                except Exception as e:
                    _logger.warning(
                        "Failed to persist Saleor GiftCard fields on %s: %s", rec.id, e
                    )

            # Sync metadata and private metadata if provided via lines
            try:
                meta_lines = rec.saleor_metadata_line_ids
                if meta_lines and remote_id:
                    metadata = [
                        {"key": line.key, "value": line.value} for line in meta_lines
                    ]
                    self._refresh_token(client)
                    client.gift_card_metadata_update(remote_id, metadata)
            except Exception as e:
                _logger.warning("Failed to update gift card metadata: %s", e)
            try:
                pmeta_lines = rec.saleor_private_metadata_line_ids
                if pmeta_lines and remote_id:
                    pmetadata = [
                        {"key": line.key, "value": line.value} for line in pmeta_lines
                    ]
                    self._refresh_token(client)
                    client.gift_card_private_metadata_update(remote_id, pmetadata)
            except Exception as e:
                _logger.warning("Failed to update gift card private metadata: %s", e)

            try:
                # Use the latest values after write for accuracy
                name_val = rec.name or saleor_display or "-"
                code_val = rec.code or saleor_code or "-"
                dash_url, obj_url = saleor_dashboard_links(
                    self.base_url,
                    "gift_card",
                    id=remote_id,
                )
                rec.message_post(
                    body=format_kv_list(
                        "Synced Gift Card:",
                        [
                            ("Account", self.email or self.name),
                            ("Name", name_val),
                            ("Code", code_val),
                            ("Saleor ID", remote_id or "-"),
                            ("Saleor", make_link("View in Saleor", obj_url)),
                        ],
                    )
                )
            except Exception as e:
                _logger.warning("Failed to post gift card sync message: %s", e)

            return bool(remote_id)
        except Exception as e:
            _logger.exception(
                "Error activating gift card '%s' via account %s: %s",
                rec.display_name,
                self.name,
                e,
            )
            raise UserError(_("Saleor gift card activation failed: %s", str(e))) from e

    def _voucher_sync_metadata(self, client, saleor_id, metadata, private_metadata):
        """Update public and private metadata if provided."""
        try:
            if metadata:
                self._refresh_token(client)
                client.voucher_metadata_update(saleor_id, metadata)
        except Exception as e:
            _logger.warning("Failed to update voucher metadata: %s", e)
        try:
            if private_metadata:
                self._refresh_token(client)
                client.voucher_private_metadata_update(saleor_id, private_metadata)
        except Exception as e:
            _logger.warning("Failed to update voucher private metadata: %s", e)

    def _voucher_resolve_and_upsert(self, client, rec, base_input, codes):
        """Find or create the voucher in Saleor and persist its ID on the record.

        Returns a tuple (saleor_id, existing) where existing is the remote voucher
        data when found by ID, else None.
        """
        saleor_id = rec.saleor_voucher_id
        existing = None
        if saleor_id:
            self._refresh_token(client)
            existing = client.voucher_get_by_id(saleor_id)
            if not existing:
                saleor_id = None
        if not saleor_id:
            # Try match by exact name
            self._refresh_token(client)
            found = client.vouchers_search_by_name(rec.name)
            if found and found.get("id"):
                saleor_id = found.get("id")

        if saleor_id:
            self._refresh_token(client)
            res = client.voucher_update(saleor_id, base_input)
            saleor_id = (res or {}).get("id") or saleor_id
        else:
            self._refresh_token(client)
            primary_code = codes[0] if codes else None
            create_input = dict(base_input)
            if primary_code:
                create_input["code"] = primary_code
            created = client.voucher_create(create_input)
            saleor_id = (created or {}).get("id")

        if saleor_id and rec.saleor_voucher_id != saleor_id:
            try:
                rec.write({"saleor_voucher_id": saleor_id})
            except Exception as e:
                _logger.warning(
                    "Failed to persist Saleor Voucher ID on %s: %s", rec.id, e
                )

        return saleor_id, existing

    def _voucher_update_channels(self, client, saleor_id, channel_listings):
        """Add and remove channel listings to match Odoo selection."""
        try:
            add_channels = []
            desired_ids = set()
            for ch in channel_listings or []:
                sid = ch.get("channelId")
                if sid:
                    desired_ids.add(sid)
                    item = {"channelId": sid}
                    if ("discountValue" in ch) and (
                        ch.get("discountValue") is not None
                    ):
                        item["discountValue"] = float(ch.get("discountValue") or 0.0)
                    if ("amount" in ch) and (ch.get("amount") is not None):
                        item["minAmountSpent"] = float(ch.get("amount") or 0.0)
                    add_channels.append(item)

            self._refresh_token(client)
            current_ids = set(client.voucher_channel_listings_get(saleor_id) or [])
            remove_ids = list(current_ids - desired_ids)

            if add_channels or remove_ids:
                self._refresh_token(client)
                client.voucher_channel_listing_update(
                    saleor_id,
                    add_channels=add_channels or [],
                    remove_channels=remove_ids or [],
                )
        except Exception as e:
            _logger.warning(
                "Failed to update voucher channel listings (add/remove): %s", e
            )

    def _voucher_attach_catalogues(self, client, saleor_id, rec):
        """Attach product/category/collection/variant restrictions if any."""
        try:
            products = [
                pt.saleor_product_id
                for pt in rec.product_template_ids
                if getattr(pt, "saleor_product_id", False)
            ]
            variants = [
                pv.saleor_variant_id
                for pv in rec.product_variant_ids
                if getattr(pv, "saleor_variant_id", False)
            ]
            collections = [
                pc.saleor_collection_id
                for pc in rec.product_collection_ids
                if getattr(pc, "saleor_collection_id", False)
            ]
            categories = [
                cat.saleor_category_id
                for cat in rec.product_category_ids
                if getattr(cat, "saleor_category_id", False)
            ]
            if any([products, variants, collections, categories]):
                self._refresh_token(client)
                client.voucher_catalogues_add(
                    saleor_id,
                    products=products,
                    collections=collections,
                    categories=categories,
                    variants=variants,
                )
        except Exception as e:
            _logger.warning("Failed to attach voucher catalogues: %s", e)

    def _voucher_add_codes(self, client, saleor_id, codes, existing):
        """Add voucher codes after creation/update."""
        try:
            codes_to_add = []
            if codes:
                if existing is None:
                    codes_to_add = codes[1:] if len(codes) > 1 else []
                else:
                    codes_to_add = codes
            if codes_to_add:
                self._refresh_token(client)
                client.voucher_update_add_codes(saleor_id, codes_to_add)
        except Exception as e:
            _logger.warning("Failed to add voucher codes: %s", e)

    # --- Promotions ---
    def job_promotion_sync(self, program_id, payload):
        """Sync a loyalty.program (program_type='saleor') to Saleor Promotion."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor promotion sync skipped for program %s"
                " on inactive account %s",
                program_id,
                self.name,
            )
            return True

        prog = self.env["loyalty.program"].browse(program_id)
        if not prog or prog.program_type != "saleor":
            return True

        client = self._get_client()
        self._refresh_token(client)

        # Create or update
        saleor_id = prog.saleor_promotion_id
        try:
            if saleor_id:
                # Verify remote exists; if missing, create new
                remote = client.promotion_get_by_id(saleor_id)
                if remote and remote.get("id"):
                    # On update, Saleor may not accept 'type' in input
                    upd_payload = dict(payload)
                    upd_payload.pop("type", None)
                    res = client.promotion_update(saleor_id, upd_payload)
                    saleor_id = (res or {}).get("id") or saleor_id
                else:
                    created = client.promotion_create(payload)
                    saleor_id = (created or {}).get("id")
            else:
                created = client.promotion_create(payload)
                saleor_id = (created or {}).get("id")

            # Persist
            if saleor_id and prog.saleor_promotion_id != saleor_id:
                prog.write({"saleor_promotion_id": saleor_id})

            # Skipping promotion channel sync per requirement

            # Sync promotion rules (upsert)
            try:
                self._sync_promotion_rules(client, prog, saleor_id)
            except Exception as e:
                _logger.warning(
                    "Failed to sync promotion rules for program %s: %s",
                    prog.display_name,
                    e,
                )

            return bool(saleor_id)

        except Exception as e:
            _logger.exception(
                "Error syncing promotion '%s' to Saleor via account %s: %s",
                prog.display_name,
                self.name,
                e,
            )
            raise UserError(_("Saleor promotion sync failed: %s", str(e))) from e

    def job_promotion_sync_batch(self, items):
        """Batch sync promotions."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor promotion batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            pid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_promotion_sync(pid, payload)
            except Exception as e:
                rec = self.env["loyalty.program"].browse(pid)
                rec_name = rec.display_name if rec else f"promotion[{pid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch promotion sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def _sync_promotion_channels(self, client, program, saleor_promotion_id):
        """Delta-sync promotion channels from program rules' channel_id."""
        # Collect desired channel IDs from rules
        rules = program.discount_rule_ids
        channels = rules.mapped("channel_id") if rules else self.env["saleor.channel"]
        desired_ids = set()
        if channels:
            missing = channels.filtered(lambda ch: not ch.saleor_channel_id)
            if missing:
                names = ", ".join(missing.mapped("display_name"))
                raise UserError(
                    _(
                        "Some channels on this promotion"
                        " are not synced to Saleor yet: %s.\n"
                        "Please sync these channels first.",
                        names,
                    )
                )
            desired_ids = {ch.saleor_channel_id for ch in channels}

        # Fetch current promotion listings
        self._refresh_token(client)
        current = client.promotion_channel_listings(saleor_promotion_id) or []
        current_ids = {
            item.get("channel", {}).get("id") for item in current if item.get("channel")
        }

        to_add_ids = sorted(list(desired_ids - current_ids))
        to_remove_ids = sorted(list(current_ids - desired_ids))

        add_channels = [{"channelId": ch_id} for ch_id in to_add_ids]

        if add_channels or to_remove_ids:
            client.promotion_channel_listing_update(
                saleor_promotion_id,
                add_channels=add_channels,
                remove_channels=to_remove_ids,
            )
        return True

    def job_attribute_sync(self, attribute_id, payload):
        return self.job_saleor_sync("attribute", attribute_id, payload)

    def job_attribute_sync_batch(self, items):
        """Batch sync product attributes."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor attribute batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            att_id = it.get("id")
            payload = it.get("payload")
            try:
                self.job_attribute_sync(att_id, payload)
            except Exception as e:
                rec = self.env["product.attribute"].browse(att_id)
                rec_name = rec.display_name if rec else f"attribute[{att_id}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch attribute sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def _channel_prepare_payload_with_zones(self, ch, payload):
        zones = ch.shipping_zone_ids
        if zones:
            missing = zones.filtered(lambda z: not z.saleor_id)
            if missing:
                names = ", ".join(missing.mapped("name"))
                raise UserError(
                    _(
                        "Some shipping zones assigned to this channel"
                        " are not synced to Saleor yet: %s."
                        "\nPlease sync these shipping zones first.",
                        names,
                    )
                )
            payload = dict(payload or {})
            payload["addShippingZones"] = [z.saleor_id for z in zones]
        return payload

    def _channel_align_currency(self, ch, remote_cur):
        local_cur = getattr(ch.currency_id, "name", None)
        if remote_cur and remote_cur != local_cur:
            cur_rec = self.env["res.currency"].search(
                [("name", "=", remote_cur)], limit=1
            )
            if cur_rec:
                ch.with_context(bypass_currency_lock=True).write(
                    {"currency_id": cur_rec.id}
                )
            else:
                _logger.warning(
                    "Currency %s not found in res.currency;" " keeping local %s",
                    remote_cur,
                    local_cur,
                )

    def _strip_channel_currency_from_payload(self, payload):
        if payload and payload.get("currencyCode") is not None:
            payload = dict(payload)
            payload.pop("currencyCode", None)
        return payload

    def _post_channel_synced_message(self, ch, slug):
        try:
            dash_url, obj_url = saleor_dashboard_links(
                self.base_url, "channel", slug=slug, id=ch.saleor_channel_id
            )
            body = format_kv_list(
                "Synced to Saleor:",
                [
                    ("Account", self.email or self.name),
                    ("Slug", slug),
                    ("Saleor ID", ch.saleor_channel_id),
                    ("Saleor", make_link("View in Saleor", obj_url)),
                ],
            )
            ch.message_post(body=body)
        except Exception as e:
            _logger.warning(
                "Failed to post channel sync message (update) on %s: %s",
                ch.id,
                e,
            )

    def _update_channel_tax_configuration(self, client, ch):
        """Best-effort update of the Saleor channel tax configuration.

        Isolated in a helper to keep job_channel_sync complexity low.
        """
        channel_id = getattr(ch, "saleor_channel_id", False)
        if not channel_id:
            return
        try:
            entered = getattr(ch, "entered_prices", "without_tax") or "without_tax"
            prices_entered_with_tax = entered == "with_tax"
            client.channel_tax_configuration_update(channel_id, prices_entered_with_tax)
        except Exception as e:
            _logger.warning(
                "Failed to update tax configuration for channel %s: %s",
                channel_id,
                e,
            )

    def job_channel_sync(self, channel_id, payload):  # noqa: C901
        """Sync a single saleor.channel to Saleor."""
        self.ensure_one()

        ch = self.env["saleor.channel"].browse(channel_id)
        if not ch:
            return True

        client = self._get_client()
        try:
            payload = self._channel_prepare_payload_with_zones(ch, payload)

            # Update if we already have an ID
            if ch.saleor_channel_id:
                # Verify the stored ID exists remotely
                self._refresh_token(client)
                remote = None
                try:
                    remote = client.channel_get_by_id(ch.saleor_channel_id)
                except Exception:
                    remote = None
                if not remote:
                    _logger.warning(
                        "Stored Saleor channel ID %s not found;"
                        " will re-create by slug %s",
                        ch.saleor_channel_id,
                        ch.slug,
                    )
                    ch.saleor_channel_id = False
                else:
                    _logger.info(
                        "Updating Saleor channel %s (%s)", ch.slug, ch.saleor_channel_id
                    )
                    try:
                        remote_cur = (remote or {}).get("currencyCode")
                        self._channel_align_currency(ch, remote_cur)
                    except Exception:
                        _logger.exception(
                            "Failed to align channel currency with Saleor"
                        )
                    payload = self._strip_channel_currency_from_payload(payload)
                    res = client.channel_update(ch.saleor_channel_id, payload)
                    # Persist and chatter
                    self._post_channel_synced_message(ch, ch.slug)
                    self._update_channel_tax_configuration(client, ch)
                    return bool(res)

            # Otherwise try to find by slug
            slug = payload.get("slug") or getattr(ch, "slug", None)
            existing = None
            if slug:
                self._refresh_token(client)
                existing = client.channel_get_by_slug(slug)

            if existing and existing.get("id"):
                ch.saleor_channel_id = existing["id"]
                _logger.info("Updating existing Saleor channel %s", slug)
                self._refresh_token(client)
                # Ensure local currency matches remote when found by slug
                try:
                    remote_cur = (existing or {}).get("currencyCode")
                    self._channel_align_currency(ch, remote_cur)
                except Exception:
                    _logger.exception(
                        "Failed to align channel currency with Saleor (slug)"
                    )
                payload = self._strip_channel_currency_from_payload(payload)
                res = client.channel_update(ch.saleor_channel_id, payload)
                self._post_channel_synced_message(ch, slug)
                self._update_channel_tax_configuration(client, ch)
                return bool(res)

            # Create new
            _logger.info("Creating Saleor channel %s", slug or ch.name)
            self._refresh_token(client)
            # Ensure currencyCode is present for creation
            if not payload.get("currencyCode"):
                cur = getattr(ch.currency_id, "name", None)
                if not cur:
                    raise UserError(
                        _(
                            "Channel %s requires a Currency before creating in Saleor",
                            ch.display_name or ch.slug or ch.name,
                        )
                    )
                payload = dict(payload)
                payload["currencyCode"] = cur
            created = client.channel_create(payload)
            ch.saleor_channel_id = (created or {}).get("id")
            try:
                self._post_channel_synced_message(ch, slug or ch.slug)
            except Exception as e:
                _logger.warning(
                    "Failed to post channel sync message (create) on %s: %s",
                    ch.id,
                    e,
                )
            if ch.saleor_channel_id:
                self._update_channel_tax_configuration(client, ch)
            return bool(ch.saleor_channel_id)

        except Exception as e:
            _logger.exception(
                "Error syncing channel '%s' to Saleor via account %s: %s",
                ch.slug,
                self.name,
                e,
            )
            try:
                ch.message_post(
                    body=format_note(
                        self.env,
                        "Error syncing to Saleor (account %s): %s",
                        self.email or self.name,
                        str(e),
                    )
                )
            except Exception as e2:
                _logger.warning(
                    "Failed to post channel sync error message on %s: %s",
                    ch.id,
                    e2,
                )
            raise UserError(_("Saleor channel sync failed: %s", e)) from e

    def job_channel_sync_batch(self, items):
        """Batch sync channels."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor channel batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            cid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_channel_sync(cid, payload)
            except Exception as e:
                rec = self.env["saleor.channel"].browse(cid)
                rec_name = rec.display_name if rec else f"channel[{cid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch channel sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def job_tax_sync(self, tax_id, payload):
        """Sync a single account.tax to Saleor TaxClass."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor tax sync skipped for tax %s" " on inactive account %s",
                tax_id,
                self.name,
            )
            return True

        tax = self.env["account.tax"].browse(tax_id)
        if not tax:
            return True

        # Make sure our app exists and has required permissions before using app token
        try:
            self._ensure_app_and_webhook()
        except Exception as e:
            _logger.warning(
                "Failed to ensure Saleor App and Webhook for account %s: %s",
                self.name,
                e,
            )

        client = self._get_client()

        saleor_tax_id = None
        error = None
        try:
            saleor_tax_id = upsert_tax_class(client, tax, payload)
            if saleor_tax_id and tax.saleor_tax_class_id != saleor_tax_id:
                tax.write({"saleor_tax_class_id": saleor_tax_id})
        except Exception as e:
            error = e
            _logger.error(
                "Error syncing tax %s to Saleor via account %s: %s",
                tax_id,
                self.name,
                str(e),
                exc_info=True,
            )

        if error:
            try:
                tax.message_post(
                    body=format_note(
                        self.env,
                        "Error syncing to Saleor (account %s): %s",
                        self.email,
                        str(error),
                    )
                )
            except Exception as e:
                _logger.warning(
                    "Failed to post error message on tax %s for account %s: %s",
                    tax_id,
                    self.email,
                    e,
                )
            return False

        try:
            dash_url, obj_url = saleor_dashboard_links(
                self.base_url, "tax", id=saleor_tax_id
            )
            body = format_kv_list(
                "Synced to Saleor successfully:",
                [
                    ("Account", self.email or self.name),
                    ("TaxClass ID", saleor_tax_id),
                    ("Saleor", make_link("View in Saleor", obj_url)),
                ],
            )
            tax.message_post(body=body)
        except Exception as e:
            _logger.warning(
                "Failed to post sync message on tax %s for account %s: %s",
                tax_id,
                self.email,
                e,
            )
        return True

    def job_tax_sync_batch(self, items):
        """Batch sync account.tax to Saleor TaxClass."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor tax batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            tid = it.get("id")
            payload = it.get("payload")
            try:
                self.job_tax_sync(tid, payload)
            except Exception as e:
                rec = self.env["account.tax"].browse(tid)
                rec_name = rec.display_name if rec else f"tax[{tid}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch tax sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def job_shipping_method_sync(self, carrier_id, payload):
        """Sync a single delivery.carrier shipping method to Saleor."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor shipping method sync skipped for carrier %s"
                " on inactive account %s",
                carrier_id,
                self.name,
            )
            return True

        carrier = self.env["delivery.carrier"].browse(carrier_id)
        if not carrier or carrier.delivery_type != "saleor":
            return True

        if not carrier.zone_id:
            _logger.warning("Carrier %s has no shipping zone assigned", carrier.name)
            return False

        if not carrier.zone_id.saleor_id:
            _logger.warning(
                "Shipping zone %s for carrier %s is not synced to Saleor",
                carrier.zone_id.name,
                carrier.name,
            )
            return False

        client = self._get_client()
        try:
            method_id = carrier.saleor_shipping_method_id
            exists = False

            if method_id:
                # Verify existence in Saleor
                self._refresh_token(client)
                exists = bool(client.shipping_method_get_by_id(method_id))

            if exists:
                method_id = self._shipping_method_update_flow(
                    client, carrier, method_id, payload
                )
            else:
                method_id = self._shipping_method_create_flow(client, carrier, payload)

            # Sync channel listings for the shipping method
            if method_id:
                try:
                    self._sync_shipping_method_channel_listings(
                        client, carrier, method_id
                    )
                except Exception as e:
                    _logger.warning(
                        "Failed to sync channel listings for carrier %s: %s",
                        carrier.name,
                        e,
                    )

            return bool(method_id)

        except Exception as e:
            _logger.exception(
                """Error syncing shipping method '%s'
                 to Saleor via account %s: %s""",
                carrier.name,
                self.name,
                e,
            )
            try:
                if carrier.zone_id:
                    carrier.zone_id.message_post(
                        body=format_note(
                            self.env,
                            "Error syncing shipping method %s to Saleor "
                            "(account %s): %s",
                            carrier.name,
                            self.email or self.name,
                            str(e),
                        )
                    )
            except Exception as e2:
                _logger.warning(
                    "Failed to post carrier sync error message on %s: %s",
                    carrier.id,
                    e2,
                )
            return False

    def _shipping_method_update_flow(self, client, carrier, method_id, payload):
        """Handle update of an existing shipping method and related data."""
        _logger.info(
            "Updating Saleor shipping method for carrier %s (%s)",
            carrier.name,
            method_id,
        )
        self._refresh_token(client)
        # Create update payload without postal codes and excluded products
        update_payload = {
            k: v
            for k, v in payload.items()
            if k not in ["addPostalCodeRules", "inclusionType", "excludedProducts"]
        }
        updated = client.shipping_method_update(method_id, update_payload)
        _logger.info(
            "Updated shipping method %s for carrier %s: %s",
            method_id,
            carrier.name,
            updated,
        )

        # Metadata
        try:
            if "metadata" in payload and payload["metadata"]:
                client.shipping_method_metadata_update(method_id, payload["metadata"])
            if "privateMetadata" in payload and payload["privateMetadata"]:
                client.shipping_method_private_metadata_update(
                    method_id, payload["privateMetadata"]
                )
        except Exception as e:
            _logger.warning(
                "Failed to update metadata for shipping method %s: %s", method_id, e
            )

        # Postal codes
        if "addPostalCodeRules" in payload:
            try:
                self._refresh_token(client)
                inclusion_type = payload.get("inclusionType", "INCLUDE")
                client.shipping_method_sync_postal_codes(
                    method_id, payload["addPostalCodeRules"], inclusion_type
                )
            except Exception as e:
                _logger.warning(
                    "Failed to sync postal codes for method %s: %s", method_id, e
                )

        # Excluded products
        if "excludedProducts" in payload:
            try:
                self._refresh_token(client)
                client.shipping_method_sync_excluded_products(
                    method_id, payload["excludedProducts"]
                )
            except Exception as e:
                _logger.warning(
                    "Failed to sync excluded products for method %s: %s", method_id, e
                )

        # Message
        try:
            if carrier.zone_id:
                dash_url, obj_url = saleor_dashboard_links(
                    self.base_url,
                    "shipping_method",
                    id=method_id,
                    zone_id=getattr(carrier.zone_id, "saleor_id", None),
                )
                carrier.zone_id.message_post(
                    body=format_kv_list(
                        "Update Shipping Method:",
                        [
                            ("Account", self.email or self.name),
                            ("Shipping Method", carrier.name),
                            ("Saleor ID", method_id),
                            ("Saleor", make_link("View in Saleor", obj_url)),
                        ],
                    )
                )
        except Exception as e:
            _logger.warning(
                "Failed to post carrier sync message (update) on %s: %s", carrier.id, e
            )

        return method_id

    def _shipping_method_create_flow(self, client, carrier, payload):
        """Handle creation of a shipping method and related data.
        Returns method_id or False."""
        _logger.info(
            "Creating Saleor shipping method for carrier %s in zone %s",
            carrier.name,
            carrier.zone_id.name,
        )
        self._refresh_token(client)
        created_method = client.shipping_method_create(
            carrier.zone_id.saleor_id, payload
        )
        method_id = (created_method or {}).get("id")
        carrier.saleor_shipping_method_id = method_id
        _logger.info(
            "Created shipping method for carrier %s -> id=%s", carrier.name, method_id
        )

        # Enforce min/max delivery days if provided
        if method_id and (
            "minimumDeliveryDays" in payload or "maximumDeliveryDays" in payload
        ):
            try:
                self._refresh_token(client)
                _logger.debug(
                    "Post-create enforcing min/max delivery days"
                    " via update for method %s",
                    method_id,
                )
                update_payload = {
                    k: v
                    for k, v in payload.items()
                    if k in ["minimumDeliveryDays", "maximumDeliveryDays"]
                }
                client.shipping_method_update(method_id, update_payload)
            except Exception as e:
                _logger.warning(
                    "Post-create update to enforce min/max delivery days"
                    " failed for method %s: %s",
                    method_id,
                    e,
                )

        # Postal codes
        if method_id and "addPostalCodeRules" in payload:
            try:
                self._refresh_token(client)
                inclusion_type = payload.get("inclusionType", "INCLUDE")
                client.shipping_method_sync_postal_codes(
                    method_id, payload["addPostalCodeRules"], inclusion_type
                )
            except Exception as e:
                _logger.warning(
                    "Failed to sync postal codes for method %s: %s", method_id, e
                )

        # Excluded products
        if method_id and "excludedProducts" in payload:
            try:
                self._refresh_token(client)
                client.shipping_method_sync_excluded_products(
                    method_id, payload["excludedProducts"]
                )
            except Exception as e:
                _logger.warning(
                    "Failed to sync excluded products for method %s: %s", method_id, e
                )

        # Message
        if not method_id:
            _logger.warning(
                "Saleor did not return an ID for created shipping method of carrier %s",
                carrier.id,
            )
            return False
        else:
            try:
                if carrier.zone_id:
                    dash_url, obj_url = saleor_dashboard_links(
                        self.base_url,
                        "shipping_method",
                        id=method_id,
                        zone_id=getattr(carrier.zone_id, "saleor_id", None),
                    )
                    carrier.zone_id.message_post(
                        body=format_kv_list(
                            "Create Shipping Method:",
                            [
                                ("Account", self.email or self.name),
                                ("Shipping Method", carrier.name),
                                ("Saleor ID", method_id),
                                ("Saleor", make_link("View in Saleor", obj_url)),
                            ],
                        )
                    )
            except Exception as e:
                _logger.warning(
                    "Failed to post carrier sync message (create) on %s: %s",
                    carrier.id,
                    e,
                )
            return method_id

    def _sync_shipping_method_channel_listings(self, client, carrier, method_id):
        """Sync channel listings for a shipping method."""
        add_channels = []

        # If carrier has specific pricing lines, use those
        if carrier.saleor_shipping_pricing_line_ids:
            for pricing_line in carrier.saleor_shipping_pricing_line_ids:
                channel = pricing_line.channel_id
                if not channel.saleor_channel_id:
                    _logger.warning(
                        "Channel %s for carrier %s is not synced to Saleor",
                        channel.name,
                        carrier.name,
                    )
                    continue

                channel_config = {
                    "channelId": channel.saleor_channel_id,
                    "price": str(pricing_line.price),
                }

                # Add order value constraints only when enabled on carrier
                if carrier.order_value:
                    for (
                        order_value_line
                    ) in carrier.saleor_order_value_line_ids.filtered(
                        lambda line, ch=channel: line.channel_id == ch
                    ):
                        if carrier.shipping_method_type == "price":
                            channel_config["minimumOrderPrice"] = str(
                                order_value_line.min_value
                            )
                            channel_config["maximumOrderPrice"] = str(
                                order_value_line.max_value
                            )
                else:
                    if carrier.shipping_method_type == "price":
                        channel_config["minimumOrderPrice"] = None
                        channel_config["maximumOrderPrice"] = None

                add_channels.append(channel_config)
        else:
            if carrier.zone_id and carrier.zone_id.channel_ids:
                default_price = "0.00"  # Default price if no pricing configured
                for channel in carrier.zone_id.channel_ids:
                    if not channel.saleor_channel_id:
                        _logger.warning(
                            "Channel %s for carrier %s is not synced to Saleor",
                            channel.name,
                            carrier.name,
                        )
                        continue

                    channel_config = {
                        "channelId": channel.saleor_channel_id,
                        "price": default_price,
                    }

                    if carrier.order_value:
                        for (
                            order_value_line
                        ) in carrier.saleor_order_value_line_ids.filtered(
                            lambda line, ch=channel: line.channel_id == ch
                        ):
                            if carrier.shipping_method_type == "price":
                                channel_config["minimumOrderPrice"] = str(
                                    order_value_line.min_value
                                )
                                channel_config["maximumOrderPrice"] = str(
                                    order_value_line.max_value
                                )
                    else:
                        if carrier.shipping_method_type == "price":
                            channel_config["minimumOrderPrice"] = None
                            channel_config["maximumOrderPrice"] = None

                    add_channels.append(channel_config)

        if add_channels:
            self._refresh_token(client)
            client.shipping_method_channel_listing_update(method_id, add_channels)
            _logger.info(
                "Updated channel listings for shipping method %s with %d channels",
                method_id,
                len(add_channels),
            )
        else:
            _logger.info("No channels to add for shipping method %s", method_id)

    def job_shipping_zone(self, shipping_zone_id, payload):  # noqa: C901
        """Sync a single saleor.shippingZone to Saleor."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor shipping zone sync skipped for zone %s"
                " on inactive account %s",
                shipping_zone_id,
                self.name,
            )
            return True

        sz = self.env["saleor.shipping.zone"].browse(shipping_zone_id)
        if not sz:
            return True

        client = self._get_client()
        try:
            # Prepare payload with validated channels
            payload = self._prepare_shipping_zone_channels(sz, payload)

            if sz.saleor_id:
                _logger.info(
                    "Updating Saleor shipping zone %s (%s)", sz.name, sz.saleor_id
                )
                self._refresh_token(client)
                try:
                    res = self._shipping_zone_update_only(client, sz, payload)
                    self._post_shipping_zone_synced(sz)
                    # Always sync shipping methods after a successful update
                    try:
                        self._sync_shipping_methods(client, sz)
                    except Exception as e:
                        _logger.exception(
                            "Error syncing shipping methods for zone %s (%s): %s",
                            sz.name,
                            sz.saleor_id,
                            e,
                        )
                    return bool(res)
                except Exception as e:
                    error_msg = str(e).lower()
                    if (
                        "not_found" in error_msg
                        or "couldn't resolve to a node" in error_msg
                    ):
                        _logger.warning(
                            "Shipping zone %s with Saleor ID %s "
                            "no longer exists; will recreate",
                            sz.name,
                            sz.saleor_id,
                        )
                        sz.saleor_id = False
                    else:
                        raise

            # Try to confirm existing by ID (if any)
            existing = None
            if sz.saleor_id:
                self._refresh_token(client)
                existing = client.shipping_zone_get_by_id(sz.saleor_id)
            if existing and (
                isinstance(existing, str) or getattr(existing, "get", None)
            ):
                sz.saleor_id = (
                    existing if isinstance(existing, str) else existing.get("id")
                )
                self._refresh_token(client)
                res = self._shipping_zone_update_only(client, sz, payload)
                self._post_shipping_zone_synced(sz)
                try:
                    self._sync_shipping_methods(client, sz)
                except Exception as e:
                    _logger.exception(
                        "Error syncing shipping methods for zone %s (%s): %s",
                        sz.name,
                        sz.saleor_id,
                        e,
                    )
                return bool(res)

            # Create new zone
            created_ok = self._shipping_zone_create_only(client, sz, payload)
            self._post_shipping_zone_synced(sz)
            if sz.saleor_id:
                try:
                    self._sync_shipping_methods(client, sz)
                except Exception as e:
                    _logger.exception(
                        "Error syncing shipping methods for newly"
                        " created zone %s (%s): %s",
                        sz.name,
                        sz.saleor_id,
                        e,
                    )
            return bool(created_ok)

        except Exception as e:
            _logger.exception(
                "Error syncing shipping zone '%s' to Saleor via account %s: %s",
                sz.name,
                self.name,
                e,
            )
            raise

    def job_shipping_zone_batch(self, items):
        """Batch sync saleor.shipping.zone records."""
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor shipping zone batch sync skipped for %s item(s)"
                " on inactive account %s",
                len(items or []),
                self.name,
            )
            return True
        errors = []
        for it in items or []:
            zone_id = it.get("id")
            payload = it.get("payload")
            try:
                self.job_shipping_zone(zone_id, payload)
            except Exception as e:
                rec = self.env["saleor.shipping.zone"].browse(zone_id)
                rec_name = rec.display_name if rec else f"shipping.zone[{zone_id}]"
                errors.append((rec_name, str(e)))
        if errors:
            header = _("Batch shipping zone sync failed for %s item(s):", len(errors))
            body = format_batch_errors_message(header, errors)
            post_to_current_job_committed(self.env, self, body)
            self.env.cr.rollback()
            raise UserError(header)
        return True

    def post_fetch_success(self, rec, object_type):
        """Post a unified success message for fetch operations."""
        try:
            if object_type == "product":
                rec.message_post(
                    body=format_note(
                        self.env,
                        "Fetched metadata from Saleor (account: %s)",
                        self.name,
                    )
                )
        except Exception as e:
            _logger.warning("Failed to post fetch message on %s: %s", object_type, e)

    # --- Internal helpers to reduce complexity ---
    def _handlers_for(self, client, object_type):
        if object_type == "collection":
            model = "product.collection"
            get_by_slug = client.collection_get_by_slug
            do_update = partial(saleor_collection_do_update, client)
            do_create = client.collection_create
        elif object_type == "product":
            model = "product.template"
            get_by_slug = client.product_get_by_slug
            do_update = partial(saleor_product_do_update, client)
            do_create = client.product_create
        elif object_type == "attribute":
            model = "product.attribute"
            get_by_slug = client.attribute_get_by_slug
            do_update = partial(saleor_attribute_do_update, client)
            do_create = client.attribute_create
        else:
            raise ValueError(f"Unsupported object_type: {object_type}")
        return model, get_by_slug, do_update, do_create

    def _sync_shipping_methods(self, client, sz):
        """Ensure delivery.carrier methods in zone are created/updated"""
        self.ensure_one()
        carriers = sz.shipping_method_ids.filtered(
            lambda c: c.delivery_type == "saleor"
        )
        if not carriers:
            carriers = self.env["delivery.carrier"].search(
                [
                    ("zone_id", "=", sz.id),
                    ("delivery_type", "=", "saleor"),
                ]
            )
        _logger.info(
            "Shipping method sync for zone %s (%s): %s carriers",
            sz.name,
            sz.saleor_id,
            len(carriers),
        )
        if not carriers:
            return True

        # Use the new job-based sync pattern
        if len(carriers) == 1:
            carrier = carriers
            payload = carrier._saleor_shipping_method_prepare_payload()
            self.job_shipping_method_sync(carrier.id, payload)
        else:
            for carrier in carriers:
                payload = carrier._saleor_shipping_method_prepare_payload()
                if hasattr(self, "with_delay"):
                    self.with_delay().job_shipping_method_sync(carrier.id, payload)
                else:
                    self.job_shipping_method_sync(carrier.id, payload)
        return True

    # --- Shipping Zone helpers (complexity extraction) ---
    def _prepare_shipping_zone_channels(self, sz, payload):
        """Validate and inject channel IDs into the payload as addChannels.
        Raises UserError if some channels are not synced yet.
        """
        channels = sz.channel_ids
        if channels:
            missing_channels = channels.filtered(lambda c: not c.saleor_channel_id)
            if missing_channels:
                names = ", ".join(missing_channels.mapped("name"))
                raise UserError(
                    _(
                        "Some channels assigned to this shipping zone"
                        " are not synced to Saleor yet: %s."
                        "\nPlease sync these channels first.",
                        names,
                    )
                )
            payload = dict(payload or {})
            payload["addChannels"] = [c.saleor_channel_id for c in channels]
        return payload

    def _inject_product_tax_class(self, client, rec, payload):
        """Ensure product's sale tax has a Saleor TaxClass and inject its ID."""
        try:
            # Prefer the first sale tax on the template
            taxes = (
                getattr(rec, "taxes_id", False)
                and rec.taxes_id
                or self.env["account.tax"]
            )
            sale_taxes = (
                taxes.filtered(lambda t: t.type_tax_use == "sale")
                if taxes
                else self.env["account.tax"]
            )
            tax = sale_taxes[:1]
            tax = tax and tax[0] or None
            if not tax:
                return payload

            saleor_tax_id = getattr(tax, "saleor_tax_class_id", None)
            if not saleor_tax_id:
                # Build tax payload and upsert
                try:
                    tax_payload = tax._saleor_prepare_tax_payload()
                except Exception as e:
                    _logger.warning(
                        "Failed to prepare Saleor tax payload for tax %s: %s",
                        tax.id,
                        e,
                    )
                    tax_payload = None
                if tax_payload:
                    # Ensure app has required permissions
                    try:
                        self._ensure_app_and_webhook()
                    except Exception as e:
                        _logger.warning(
                            "Failed to ensure Saleor App and Webhook"
                            " before upserting tax %s: %s",
                            tax.id,
                            e,
                        )
                    saleor_tax_id = upsert_tax_class(client, tax, tax_payload)
                    if (
                        saleor_tax_id
                        and getattr(tax, "saleor_tax_class_id", None) != saleor_tax_id
                    ):
                        try:
                            tax.write({"saleor_tax_class_id": saleor_tax_id})
                        except Exception as e:
                            _logger.warning(
                                "Failed to store Saleor TaxClass ID on tax %s: %s",
                                tax.id,
                                e,
                            )

            if saleor_tax_id:
                payload = dict(payload or {})
                payload["taxClass"] = saleor_tax_id
        except Exception as e:
            _logger.warning(
                "Failed to resolve/create tax class for product %s: %s",
                getattr(rec, "id", "unknown"),
                e,
            )
        return payload

    def _inject_product_type_tax_class(self, client, ptype, payload):
        """Ensure product type's sale tax has a Saleor TaxClass and inject its ID."""
        try:
            tax = getattr(ptype, "tax_id", None)
            if not tax:
                return payload

            saleor_tax_id = getattr(tax, "saleor_tax_class_id", None)
            if not saleor_tax_id:
                try:
                    tax_payload = tax._saleor_prepare_tax_payload()
                except Exception as e:
                    _logger.warning(
                        "Failed to prepare Saleor tax payload for tax %s: %s",
                        tax.id,
                        e,
                    )
                    tax_payload = None
                if tax_payload:
                    try:
                        self._ensure_app_and_webhook()
                    except Exception as e:
                        _logger.warning(
                            "Failed to ensure Saleor App and Webhook"
                            " before upserting tax %s: %s",
                            tax.id,
                            e,
                        )
                    saleor_tax_id = upsert_tax_class(client, tax, tax_payload)
                    if (
                        saleor_tax_id
                        and getattr(tax, "saleor_tax_class_id", None) != saleor_tax_id
                    ):
                        try:
                            tax.write({"saleor_tax_class_id": saleor_tax_id})
                        except Exception as e:
                            _logger.warning(
                                "Failed to store Saleor TaxClass ID on tax %s: %s",
                                tax.id,
                                e,
                            )

            if saleor_tax_id:
                payload = dict(payload or {})
                payload["taxClass"] = saleor_tax_id
        except Exception as e:
            _logger.warning(
                "Failed to resolve/create tax class for product type %s: %s",
                getattr(ptype, "id", "unknown"),
                e,
            )
        return payload

    def _shipping_zone_update_only(self, client, sz, payload):
        """Update an existing shipping zone, handling metadata separately."""
        # Create update payload without metadata fields
        update_payload = {
            k: v for k, v in payload.items() if k not in ["metadata", "privateMetadata"]
        }
        res = client.shipping_zone_update(sz.saleor_id, update_payload)

        # Handle metadata updates
        try:
            if "metadata" in payload and payload["metadata"]:
                client.shipping_zone_metadata_update(sz.saleor_id, payload["metadata"])
            if "privateMetadata" in payload and payload["privateMetadata"]:
                client.shipping_zone_private_metadata_update(
                    sz.saleor_id, payload["privateMetadata"]
                )
        except Exception as e:
            _logger.warning(
                "Failed to update metadata for shipping zone %s: %s", sz.saleor_id, e
            )
        return res

    def _shipping_zone_create_only(self, client, sz, payload):
        """Create a shipping zone, then set metadata if provided. Returns True/False."""
        _logger.info("Creating Saleor shipping zone %s", sz.name)
        self._refresh_token(client)
        create_payload = {
            k: v for k, v in payload.items() if k not in ["metadata", "privateMetadata"]
        }
        created = client.shipping_zone_create(create_payload)
        sz.saleor_id = (created or {}).get("id")

        if sz.saleor_id:
            try:
                if "metadata" in payload and payload["metadata"]:
                    client.shipping_zone_metadata_update(
                        sz.saleor_id, payload["metadata"]
                    )
                if "privateMetadata" in payload and payload["privateMetadata"]:
                    client.shipping_zone_private_metadata_update(
                        sz.saleor_id, payload["privateMetadata"]
                    )
            except Exception as e:
                _logger.warning(
                    "Failed to update metadata for new shipping zone %s: %s",
                    sz.saleor_id,
                    e,
                )
        return bool(sz.saleor_id)

    def _post_shipping_zone_synced(self, sz):
        """Post a standardized message indicating the zone has been synced."""
        try:
            acc = self.email or self.name
            dash_url, obj_url = saleor_dashboard_links(
                self.base_url, "shipping_zone", id=sz.saleor_id
            )
            body = format_kv_list(
                "Synced to Saleor:",
                [
                    ("Account", acc),
                    ("Name", sz.name),
                    ("Saleor ID", sz.saleor_id),
                    ("Saleor", make_link("View in Saleor", obj_url)),
                ],
            )
            sz.message_post(body=body)
        except Exception as e:
            _logger.warning(
                "Failed to post shipping zone sync message on %s: %s", sz.id, e
            )

    def _ensure_slug_in_payload(self, rec, payload):
        slug = payload.get("slug")
        if not slug:
            name = payload.get("name") or getattr(rec, "name", None)
            if name:
                # Prefer an existing slug stored on the record, falling back
                # to generating a new one using our shared helper.
                field_name = None
                for candidate in ("saleor_slug", "saleor_collection_slug", "slug"):
                    if hasattr(rec, candidate):
                        field_name = candidate
                        break

                if field_name:
                    slug = getattr(rec, field_name, None)
                    if not slug:
                        slug = generate_unique_slug(
                            rec,
                            name,
                            slug_field_name=field_name,
                        )
                        # Persist back to the record when we own the field
                        try:
                            setattr(rec, field_name, slug)
                        except Exception as e:
                            _logger.debug(
                                "Failed to persist slug '%s' to field %s on %s: %s",
                                slug,
                                field_name,
                                getattr(rec, "id", "<no id>"),
                                e,
                            )

                if slug:
                    payload = dict(payload)
                    payload["slug"] = slug
        return slug, payload

    def _inject_product_category(self, client, rec, payload):
        """Ensure product's category exists in Saleor and inject its ID."""
        try:
            cat = rec.categ_id
            cat_id = getattr(cat, "saleor_category_id", None)
            if not cat_id:
                name = getattr(cat, "name", None)
                cat_slug = getattr(cat, "saleor_slug", None)
                if not cat_slug and name:
                    cat_slug = generate_unique_slug(
                        cat,
                        name,
                        slug_field_name="saleor_slug",
                    )
                    try:
                        cat.saleor_slug = cat_slug
                    except Exception as e:
                        _logger.debug(
                            "Failed to persist generated category slug '%s' on %s: %s",
                            cat_slug,
                            getattr(cat, "id", "<no id>"),
                            e,
                        )
                self._refresh_token(client)
                saleor_cat = client.category_get_by_slug(cat_slug) if cat_slug else None
                if not saleor_cat:
                    payload_cat = cat._saleor_prepare_payload()
                    # Ensure payload has a slug consistent with the record
                    if not payload_cat.get("slug") and cat_slug:
                        payload_cat = dict(payload_cat)
                        payload_cat["slug"] = cat_slug
                    self._refresh_token(client)
                    saleor_cat = client.category_create(payload_cat)
                cat_id = saleor_cat and saleor_cat.get("id")
                if cat_id:
                    try:
                        cat.write({"saleor_category_id": cat_id})
                    except Exception as e:
                        _logger.warning(
                            "Failed to store Saleor category ID on Odoo "
                            "category %s: %s",
                            cat.id,
                            e,
                        )
            if cat_id:
                payload = dict(payload)
                payload["category"] = cat_id
        except Exception as e:
            _logger.warning(
                "Failed to resolve/create category for product %s: %s",
                rec.id,
                e,
            )
        return payload

    def _upload_product_image(
        self,
        client,
        saleor_id,
        filename,
        img_bytes,
        content_type,
        image_record=None,
    ):
        """Upload a product image to Saleor."""
        if not (saleor_id and img_bytes and filename):
            return False

        try:
            self._refresh_token(client)

            # First, upload the image
            media_res = client.product_media_create(
                saleor_id, filename, img_bytes, content_type
            )

            if not media_res or not media_res.get("id"):
                return False

            # Update the image record with the Saleor ID if provided
            if image_record and hasattr(image_record, "saleor_image_id"):
                image_record.saleor_image_id = media_res["id"]

                # Post success message to the product's chatter
                try:
                    product_tmpl = image_record.product_tmpl_id
                    if product_tmpl:
                        product_tmpl.message_post(
                            body=format_note(
                                self.env,
                                "Successfully uploaded image '%s' to Saleor "
                                "(account %s)",
                                image_record.name,
                                self.email,
                            )
                        )
                except Exception as e:
                    _logger.warning(
                        "Failed to post image upload message for product %s: %s",
                        product_tmpl.id if product_tmpl else "unknown",
                        str(e),
                    )

            return media_res["id"]

        except Exception as e:
            _logger.warning("Failed to upload product image: %s", e, exc_info=True)
            return False

    def _upload_collection_image(
        self, client, saleor_id, filename, img_bytes, content_type
    ):
        if not (saleor_id and img_bytes and filename):
            return False
        try:
            self._refresh_token(client)
            client.collection_update(
                saleor_id,
                {},
                filename=filename,
                file_bytes=img_bytes,
                content_type=content_type,
            )
            return True
        except Exception as e:
            _logger.warning("Failed to upload collection image: %s", e)
            return False

    def _delete_product_image(self, client, saleor_image_id):
        """Delete a product image from Saleor"""
        if not saleor_image_id:
            return False

        try:
            self._refresh_token(client)
            client.product_media_delete(saleor_image_id)
            return True
        except Exception as e:
            _logger.error(
                "Failed to delete product image from Saleor: %s", str(e), exc_info=True
            )
            return False

    def _ensure_collection_and_add_product(self, client, rec, saleor_id):
        try:
            col = rec.saleor_collection_id
            name = getattr(col, "name", None)
            col_slug = getattr(col, "saleor_collection_slug", None)
            if not col_slug and name:
                # Generate and persist a slug for the collection if missing
                col_slug = generate_unique_slug(
                    col,
                    name,
                    slug_field_name="saleor_collection_slug",
                )
                try:
                    col.saleor_collection_slug = col_slug
                except Exception as e:
                    _logger.debug(
                        "Failed to persist generated collection slug '%s' on %s: %s",
                        col_slug,
                        getattr(col, "id", "<no id>"),
                        e,
                    )
            self._refresh_token(client)
            saleor_col = client.collection_get_by_slug(col_slug) if col_slug else None
            if not saleor_col:
                payload_col = col._saleor_collection_prepare_payload()
                if not payload_col.get("slug") and col_slug:
                    payload_col = dict(payload_col)
                    payload_col["slug"] = col_slug
                self._refresh_token(client)
                saleor_col = client.collection_create(payload_col)
            col_id = saleor_col and saleor_col.get("id")
            if col_id:
                self._refresh_token(client)
                client.collection_add_products(col_id, [saleor_id])
        except Exception as e:
            _logger.warning("Failed to add product %s to collection: %s", saleor_id, e)

    def _handle_attribute_values_sync(self, client, saleor_id, payload):
        """Handle syncing attribute values for an existing attribute."""
        try:
            desired = set(payload.get("values") or [])
            current = set(client.attribute_values_list(saleor_id))
            for name in sorted(desired - current):
                self._refresh_token(client)
                client.attribute_value_create(saleor_id, name)
        except Exception as e:
            _logger.warning("Failed to sync attribute values: %s", e)

    def _ensure_product_type(self, client, rec, payload):  # noqa: C901
        """Ensure ProductType exists/updates in Saleor using rec.product_type_id."""
        # Require explicit product_type_id on template
        ptype = getattr(rec, "product_type_id", None)
        if not ptype:
            raise UserError(
                _("Please set Product Type on the product before syncing to Saleor.")
            )

        # Build ProductType input payload from ptype
        input_data = self._build_product_type_input(ptype)
        input_data = self._inject_product_type_tax_class(client, ptype, input_data)

        # Create or update depending on whether a mapping already exists
        ptype_id = getattr(ptype, "saleor_product_type_id", None)
        self._refresh_token(client)
        if ptype_id:
            try:
                updated = client.product_type_update(ptype_id, input_data)
                ptype_id = (updated or {}).get("id") or ptype_id
            except Exception as e:
                _logger.warning(
                    "Saleor productTypeUpdate failed for %s: %s", ptype_id, e
                )
        else:
            existing = None
            try:
                if ptype.name:
                    existing = client.product_type_search_by_name(ptype.name)
            except Exception as e:
                _logger.warning(
                    "Saleor productType search by name failed for %s: %s", ptype.name, e
                )

            if existing and existing.get("id"):
                ptype_id = existing.get("id")
            else:
                try:
                    created = client.product_type_create(input_data)
                    ptype_id = created and created.get("id")
                except Exception as e:
                    _logger.warning(
                        "Saleor productTypeCreate failed for %s: %s", ptype.name, e
                    )

        if not ptype_id:
            raise UserError(
                _("Failed to create/update Product Type '%s' in Saleor.", ptype.name)
            )

        # Persist mapping on the product type record
        try:
            if getattr(ptype, "saleor_product_type_id", None) != ptype_id:
                ptype.write({"saleor_product_type_id": ptype_id})
        except Exception as e:
            _logger.warning(
                "Failed to store Product Type mapping on %s: %s", ptype.id, e
            )

        # Sync metadata and private metadata for ProductType via dedicated mutations
        try:
            meta_lines = getattr(ptype, "metadate_line", None)
            metadata = (
                [{"key": line.key, "value": line.value} for line in meta_lines]
                if meta_lines
                else []
            )
            if metadata:
                self._refresh_token(client)
                client.product_type_metadata_update(ptype_id, metadata)
        except Exception as e:
            _logger.warning(
                "Failed to sync public metadata for product type %s: %s", ptype.id, e
            )
        try:
            priv_lines = getattr(ptype, "private_metadata_line", None)
            private_metadata = (
                [{"key": line.key, "value": line.value} for line in priv_lines]
                if priv_lines
                else []
            )
            if private_metadata:
                self._refresh_token(client)
                client.product_type_private_metadata_update(ptype_id, private_metadata)
        except Exception as e:
            _logger.warning(
                "Failed to sync private metadata for product type %s: %s", ptype.id, e
            )

        # Update payload with product type
        new_payload = dict(payload)
        new_payload["productType"] = ptype_id
        return new_payload

    def sync_product_type_from_ptype(self, ptype):  # noqa: C901
        self.ensure_one()
        client = self._get_client()
        input_data = self._build_product_type_input(ptype)
        input_data = self._inject_product_type_tax_class(client, ptype, input_data)

        ptype_id = getattr(ptype, "saleor_product_type_id", None)
        self._refresh_token(client)
        if ptype_id:
            try:
                updated = client.product_type_update(ptype_id, input_data)
                ptype_id = (updated or {}).get("id") or ptype_id
            except Exception as e:
                _logger.warning(
                    "Saleor productTypeUpdate failed for %s: %s", ptype_id, e
                )
        else:
            existing = None
            try:
                if ptype.name:
                    existing = client.product_type_search_by_name(ptype.name)
            except Exception as e:
                _logger.warning(
                    "Saleor productType search by name failed for %s: %s",
                    ptype.name,
                    e,
                )

            if existing and existing.get("id"):
                ptype_id = existing.get("id")
            else:
                try:
                    created = client.product_type_create(input_data)
                    ptype_id = created and created.get("id")
                except Exception as e:
                    _logger.warning(
                        "Saleor productTypeCreate failed for %s: %s", ptype.name, e
                    )

        if not ptype_id:
            raise UserError(
                _(
                    "Failed to create/update Product Type '%s' in Saleor.",
                    ptype.name,
                )
            )

        try:
            if getattr(ptype, "saleor_product_type_id", None) != ptype_id:
                ptype.write({"saleor_product_type_id": ptype_id})
        except Exception as e:
            _logger.warning(
                "Failed to store Product Type mapping on %s: %s", ptype.id, e
            )

        try:
            meta_lines = getattr(ptype, "metadate_line", None)
            metadata = (
                [{"key": line.key, "value": line.value} for line in meta_lines]
                if meta_lines
                else []
            )
            if metadata:
                self._refresh_token(client)
                client.product_type_metadata_update(ptype_id, metadata)
        except Exception as e:
            _logger.warning(
                "Failed to sync public metadata for product type %s: %s", ptype.id, e
            )
        try:
            priv_lines = getattr(ptype, "private_metadata_line", None)
            private_metadata = (
                [{"key": line.key, "value": line.value} for line in priv_lines]
                if priv_lines
                else []
            )
            if private_metadata:
                self._refresh_token(client)
                client.product_type_private_metadata_update(ptype_id, private_metadata)
        except Exception as e:
            _logger.warning(
                "Failed to sync private metadata for product type %s: %s", ptype.id, e
            )

    def _build_product_type_input(self, ptype):
        """Map saleor.product.type fields to Saleor ProductTypeInput."""
        # kind mapping
        kind_map = {
            "normal": "NORMAL",
            "gift_card": "GIFT_CARD",
        }
        kind_val = kind_map.get(getattr(ptype, "kind", None) or "normal", "NORMAL")

        # attributes mapping (require Saleor IDs on attributes)
        prod_attrs = []
        if getattr(ptype, "product_attribute_ids", None):
            prod_attrs = [
                a.saleor_attribute_id
                for a in ptype.product_attribute_ids
                if getattr(a, "saleor_attribute_id", None)
            ]
        var_attrs = []
        if getattr(ptype, "variant_attribute_ids", None):
            var_attrs = [
                a.saleor_attribute_id
                for a in ptype.variant_attribute_ids
                if getattr(a, "saleor_attribute_id", None)
            ]

        # flags
        has_variants = bool(
            getattr(ptype, "use_variant_attributes", False) and var_attrs
        )
        is_shipping_required = bool(getattr(ptype, "is_shipping", False))

        # optional tax fields: keep None if not mapped in Odoo
        tax_class = None
        tax_code = None

        # weight: include only if positive
        weight_val = getattr(ptype, "weight", 0) or 0
        weight = weight_val if weight_val > 0 else None

        return {
            "name": ptype.name,
            "slug": getattr(ptype, "slug", None) or None,
            "kind": kind_val,
            "hasVariants": has_variants,
            "isDigital": False,
            "isShippingRequired": is_shipping_required,
            "productAttributes": prod_attrs,
            "variantAttributes": var_attrs,
            "taxClass": tax_class,
            "taxCode": tax_code,
            "weight": weight,
        }

    def _persist_saleor_id(self, rec, object_type, saleor_id):
        """Persist Saleor ID on the Odoo record."""
        if not saleor_id:
            return

        field_map = {
            "product": ("saleor_product_id", "saleor_product_id"),
            "attribute": ("saleor_attribute_id", "saleor_attribute_id"),
            "collection": ("saleor_collection_id", "saleor_collection_id"),
            "category": ("saleor_category_id", "saleor_category_id"),
        }

        field_name, current_value = field_map.get(object_type, (None, None))
        if not field_name:
            return

        try:
            if getattr(rec, current_value, None) != saleor_id:
                rec.write({field_name: saleor_id})
        except Exception as e:
            _logger.warning("Failed to store Saleor %s ID on Odoo: %s", object_type, e)

    def _handle_image_upload(
        self,
        client,
        object_type,
        saleor_id,
        filename,
        img_bytes,
        content_type,
        image_record=None,
    ):
        """Handle image upload based on object type."""
        if not all([saleor_id, filename, img_bytes, content_type]):
            _logger.warning("Missing required parameters for image upload")
            return False

        try:
            upload_methods = {
                "product": self._upload_product_image,
                "collection": self._upload_collection_image,
            }

            if object_type in upload_methods:
                if object_type == "product":
                    return upload_methods[object_type](
                        client=client,
                        saleor_id=saleor_id,
                        filename=filename,
                        img_bytes=img_bytes,
                        content_type=content_type,
                        image_record=image_record,
                    )
                else:
                    return upload_methods[object_type](
                        client, saleor_id, filename, img_bytes, content_type
                    )
            return False
        except Exception as e:
            _logger.error("Error uploading image to Saleor: %s", str(e), exc_info=True)
            return False

    def _process_image_upload(
        self,
        client,
        object_type,
        saleor_id,
        img_bytes,
        filename,
        content_type,
        image_record=None,
    ):
        """Handle the upload of a single image to Saleor."""
        if not all([saleor_id, img_bytes, filename, content_type]):
            return False

        return self._handle_image_upload(
            client=client,
            object_type=object_type,
            saleor_id=saleor_id,
            filename=filename,
            img_bytes=img_bytes,
            content_type=content_type,
            image_record=image_record,
        )

    def _process_extra_images(self, client, object_type, saleor_id, rec):
        """Process and upload extra product images."""
        extra_images = self._prepare_image(rec, extra_images=True) or []
        if not isinstance(extra_images, list):
            extra_images = []

        for img_data in extra_images:
            if not isinstance(img_data, list | tuple) or len(img_data) < 6:
                continue

            try:
                img_bytes = img_data[0]
                filename = (
                    str(img_data[1]) if img_data[1] else f"image_{int(time.time())}.jpg"
                )
                content_type = str(img_data[2]) if img_data[2] else "image/jpeg"
                image_record = img_data[5] if len(img_data) > 5 else None

                if not all([img_bytes, filename, content_type]):
                    continue

                if not (image_record and image_record.saleor_image_id):
                    self._process_image_upload(
                        client=client,
                        object_type=object_type,
                        saleor_id=saleor_id,
                        img_bytes=img_bytes,
                        filename=filename,
                        content_type=content_type,
                        image_record=image_record,
                    )
            except (IndexError, ValueError, TypeError) as e:
                _logger.warning("Skipping invalid image data: %s", e)
                continue

    def _handle_deleted_images(self, client, rec, payload):
        """Handle deletion of images that were removed from the product."""
        current_image_ids = set(
            rec.saleor_image_ids.filtered("saleor_image_id").mapped("saleor_image_id")
        )
        previous_image_ids = set(payload.get("_saleor_current_image_ids", []))
        deleted_image_ids = previous_image_ids - current_image_ids

        for image_id in deleted_image_ids:
            try:
                if self._delete_product_image(client, image_id):
                    _logger.info("Successfully deleted image %s from Saleor", image_id)
                    rec.message_post(
                        body=format_note(
                            self.env,
                            "Deleted image from Saleor (ID: %s, account: %s)",
                            image_id,
                            self.email,
                        )
                    )
            except Exception as e:
                _logger.error(
                    "Failed to delete image %s from Saleor: %s", image_id, str(e)
                )

    def _update_existing_record(
        self,
        client,
        object_type,
        rec,
        payload,
        existing,
        img_bytes,
        filename,
        content_type,
    ):
        """Handle update of an existing record in Saleor."""
        if object_type == "product":
            payload = self._ensure_product_type(client, rec, payload)
        self._refresh_token(client)
        res = self._handlers_for(client, object_type)[2](
            existing["id"], payload, filename, img_bytes, content_type
        )
        saleor_id = (res or {}).get("id") or existing.get("id")

        if object_type == "attribute":
            self._handle_attribute_values_sync(client, saleor_id, payload)

        return saleor_id

    def _create_new_record(
        self, client, object_type, rec, payload, img_bytes, filename, content_type
    ):
        """Handle creation of a new record in Saleor."""
        if object_type == "product":
            payload = self._ensure_product_type(client, rec, payload)

        self._refresh_token(client)
        res = self._handlers_for(client, object_type)[3](payload)
        saleor_id = (res or {}).get("id")

        if object_type == "attribute" and saleor_id:
            self._persist_saleor_id(rec, object_type, saleor_id)

        return saleor_id

    def job_saleor_fetch(self, record_ids, model_name):
        """Dispatcher job to fetch metadata based on model_name.

        Accepts a single ID or a list of IDs and iterates accordingly.
        """
        self.ensure_one()

        ids = record_ids if isinstance(record_ids, list | tuple) else [record_ids]
        overall = True
        for record_id in ids:
            _logger.info(
                "Starting Saleor metadata fetch for %s ID %s", model_name, record_id
            )
            if model_name == "product.template":
                ok = self.job_product_metadata_fetch(record_id)
                overall = overall and bool(ok)
            else:
                _logger.error("Unsupported model for fetch: %s", model_name)
                overall = False
        return overall

    def job_product_metadata_fetch(self, product_tmpl_id):
        """Fetch metadata for a product.template record."""
        self.ensure_one()
        model_name = "product.template"
        product = self.env[model_name].browse(product_tmpl_id)
        if not product.exists():
            _logger.error("Record %s with ID %s not found", model_name, product_tmpl_id)
            return False

        # Validate inputs
        if not getattr(product, "saleor_product_id", False):
            msg = f"Product {product.id} is not synced with Saleor yet"
            _logger.error(msg)
            product.message_post(
                body=msg, message_type="comment", subtype_xmlid="mail.mt_note"
            )
            return False

        try:
            client = self._get_client()
            self._refresh_token(client)

            # GraphQL query
            query = """
                query Product($id: ID!) {
                    product(id: $id) {
                        metadata { key value }
                        privateMetadata { key value }
                    }
                }
                """
            variables = {"id": product.saleor_product_id}
            result = client.graphql(query, variables)

            if not result or not result.get("product"):
                raise Exception("Invalid response from Saleor")

            product_data = result["product"]
            metadata = product_data.get("metadata", [])
            private_metadata = product_data.get("privateMetadata", [])

            # Clear existing lines
            product.saleor_product_metadata_line_ids.unlink()
            if hasattr(product, "saleor_product_private_metadata_line_ids"):
                product.saleor_product_private_metadata_line_ids.unlink()

            # Build new lines
            metadata_lines = [
                (0, 0, {"key": it.get("key", ""), "value": it.get("value", "")})
                for it in metadata
            ]
            update_vals = {"saleor_product_metadata_line_ids": metadata_lines}
            if hasattr(product, "saleor_product_private_metadata_line_ids"):
                private_lines = [
                    (0, 0, {"key": it.get("key", ""), "value": it.get("value", "")})
                    for it in private_metadata
                ]
                update_vals["saleor_product_private_metadata_line_ids"] = private_lines

            # Write and mark status
            product.write({**update_vals, "is_metadata_fetched": True})

            # Notify
            self.post_fetch_success(product, "product")
            _logger.info(
                "Fetched metadata from Saleor for product_tmpl %s via account %s",
                product.id,
                self.name,
            )
            return True

        except Exception as e:
            _logger.error(
                "Error fetching metadata from Saleor for %s ID %s: %s",
                model_name,
                product_tmpl_id,
                str(e),
                exc_info=True,
            )
            product.message_post(
                body=f"Error fetching metadata from Saleor: {str(e)}",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return False

    def job_saleor_sync(self, object_type, record_id, payload):
        """Generic Saleor sync job for supported object types.

        object_type: 'collection' | 'product'
        record_id: record id of the corresponding Odoo model
        payload: dict prepared from the record
        """
        self.ensure_one()
        if not self.active:
            _logger.debug(
                "Saleor %s job skipped for record %s on inactive account %s",
                object_type,
                record_id,
                self.name,
            )
            return True

        client = self._get_client()
        (
            rec,
            slug,
            payload,
            existing,
            img_bytes,
            filename,
            content_type,
        ) = self._job_saleor_prepare_sync(client, object_type, record_id, payload)

        saleor_id = self._job_saleor_upsert_record(
            client,
            object_type,
            rec,
            payload,
            existing,
            img_bytes,
            filename,
            content_type,
        )

        img_uploaded = False
        img_uploaded = self._job_saleor_post_upsert(
            client,
            object_type,
            rec,
            payload,
            saleor_id,
            slug,
            img_bytes,
            filename,
            content_type,
        )

        self._post_success(
            rec,
            object_type,
            slug,
            payload,
            saleor_id,
            img_uploaded=img_uploaded,
            img_bytes=img_bytes,
        )
        return True

    def _job_saleor_prepare_sync(self, client, object_type, record_id, payload):
        model, get_by_slug, _, _ = self._handlers_for(client, object_type)
        rec = self.env[model].browse(record_id)

        slug, payload = self._ensure_slug_in_payload(rec, payload)
        self._refresh_token(client)
        existing = get_by_slug(slug) if slug else None

        img_bytes, filename, content_type = self._prepare_image(rec)
        if object_type == "product" and getattr(rec, "categ_id", False):
            payload = self._inject_product_category(client, rec, payload)
        if object_type == "product":
            payload = self._inject_product_tax_class(client, rec, payload)

        return rec, slug, payload, existing, img_bytes, filename, content_type

    def _job_saleor_upsert_record(
        self,
        client,
        object_type,
        rec,
        payload,
        existing,
        img_bytes,
        filename,
        content_type,
    ):
        if existing and existing.get("id"):
            saleor_id = self._update_existing_record(
                client,
                object_type,
                rec,
                payload,
                existing,
                img_bytes,
                filename,
                content_type,
            )
        else:
            saleor_id = self._create_new_record(
                client,
                object_type,
                rec,
                payload,
                img_bytes,
                filename,
                content_type,
            )
        self._persist_saleor_id(rec, object_type, saleor_id)
        return saleor_id

    def _job_saleor_post_upsert(
        self,
        client,
        object_type,
        rec,
        payload,
        saleor_id,
        slug,
        img_bytes,
        filename,
        content_type,
    ):
        img_uploaded = False

        if object_type == "collection" and saleor_id:
            self._job_saleor_sync_collection_channels(client, rec, saleor_id)

        if object_type == "product" and saleor_id:
            self._job_saleor_sync_product_channels(client, rec, saleor_id)
            img_uploaded = self._job_saleor_process_product_images(
                client,
                rec,
                payload,
                saleor_id,
                img_bytes,
                filename,
                content_type,
            )
            self._job_saleor_auto_sync_single_variant(rec)

        if "_saleor_current_image_ids" in payload:
            del payload["_saleor_current_image_ids"]

        self._job_saleor_persist_slug(object_type, rec, slug)
        return img_uploaded

    def _job_saleor_sync_collection_channels(self, client, rec, saleor_id):
        try:
            self._sync_collection_channel_listings(client, rec, saleor_id)
        except Exception as e:
            _logger.warning(
                "Failed to sync collection channel listings for %s: %s",
                rec.display_name,
                e,
            )

    def _job_saleor_sync_product_channels(self, client, rec, saleor_id):
        try:
            self._sync_product_channel_listings(client, rec, saleor_id)
        except Exception as e:
            _logger.warning(
                "Failed to sync product channel listings for %s: %s",
                rec.display_name,
                e,
            )

    def _job_saleor_process_product_images(
        self,
        client,
        rec,
        payload,
        saleor_id,
        img_bytes,
        filename,
        content_type,
    ):
        img_uploaded = False
        if img_bytes and filename and content_type:
            img_uploaded = self._process_image_upload(
                client=client,
                object_type="product",
                saleor_id=saleor_id,
                img_bytes=img_bytes,
                filename=filename,
                content_type=content_type,
            )

        self._process_extra_images(client, "product", saleor_id, rec)

        if getattr(rec, "saleor_collection_id", False):
            self._ensure_collection_and_add_product(client, rec, saleor_id)

        self._handle_deleted_images(client, rec, payload)
        return img_uploaded

    def _job_saleor_auto_sync_single_variant(self, rec):
        try:
            tmpl = rec
            variants = getattr(tmpl, "product_variant_ids", False)
            if variants and len(variants) == 1 and tmpl.saleor_product_id:
                variant = variants[0]
                if variant.default_code:
                    variant_payload = variant._saleor_prepare_variant_payload(
                        tmpl.saleor_product_id
                    )
                    if hasattr(self, "with_delay"):
                        self.with_delay().job_product_variant_sync(
                            variant.id,
                            tmpl.saleor_product_id,
                            variant_payload,
                        )
                    else:
                        self.job_product_variant_sync(
                            variant.id,
                            tmpl.saleor_product_id,
                            variant_payload,
                        )
        except Exception as e:
            _logger.warning(
                "Failed to auto-sync single variant for product %s: %s",
                getattr(rec, "display_name", getattr(rec, "id", "-")),
                e,
            )

    def _job_saleor_persist_slug(self, object_type, rec, slug):
        try:
            if (
                object_type == "product"
                and slug
                and hasattr(rec, "saleor_slug")
                and rec.saleor_slug != slug
            ):
                rec.write({"saleor_slug": slug})
        except Exception as e:
            _logger.warning(
                "Failed to persist slug '%s' on %s[%s]: %s",
                slug,
                object_type,
                getattr(rec, "id", "-"),
                e,
            )

    def _sync_collection_channel_listings(
        self, client, collection_rec, saleor_collection_id
    ):
        """Ensure the collection has channel listings matching Odoo channels.

        - addChannels: channels present in Odoo but missing in Saleor
        - removeChannels: channels present in Saleor but not in Odoo
        Keeps unchanged listings intact.
        Requires channels to be synced to Saleor first (have saleor_channel_id).
        """
        channels = getattr(collection_rec, "channel_ids", False)
        if not channels:
            # If no channels in Odoo, remove all current listings
            self._refresh_token(client)
            current = client.collection_channel_listings(saleor_collection_id) or []
            current_ids = [
                item.get("channel", {}).get("id")
                for item in current
                if item.get("channel")
            ]
            if current_ids:
                client.collection_channel_listing_update(
                    saleor_collection_id,
                    add_channels=[],
                    remove_channels=current_ids,
                )
            return True
        missing = channels.filtered(lambda ch: not ch.saleor_channel_id)
        if missing:
            names = ", ".join(missing.mapped("display_name"))
            raise UserError(
                _(
                    "Some channels on this collection"
                    " are not synced to Saleor yet: %s.\n"
                    "Please sync these channels first.",
                    names,
                )
            )
        # Build desired Saleor channel IDs from Odoo
        desired_ids = {ch.saleor_channel_id for ch in channels}

        # Fetch current listings from Saleor
        self._refresh_token(client)
        current = client.collection_channel_listings(saleor_collection_id) or []
        current_ids = {
            item.get("channel", {}).get("id") for item in current if item.get("channel")
        }

        # Compute deltas
        to_add_ids = sorted(list(desired_ids - current_ids))
        to_remove_ids = sorted(list(current_ids - desired_ids))

        add_channels = [
            {
                "channelId": ch_id,
                # Default behavior: publish
                "isPublished": True,
            }
            for ch_id in to_add_ids
        ]

        if add_channels or to_remove_ids:
            client.collection_channel_listing_update(
                saleor_collection_id,
                add_channels=add_channels,
                remove_channels=to_remove_ids,
            )
        return True

    def _sync_product_channel_listings(self, client, product_rec, saleor_product_id):
        """Delta-sync product channel listings to match Odoo template channels.

        - updateChannels: channels in Odoo but missing in Saleor
        - removeChannels: channels present in Saleor but not in Odoo
        Keeps unchanged listings intact. Requires channels to have saleor_channel_id.
        """
        channels = getattr(product_rec, "channel_ids", False)
        # Build desired IDs set
        desired_ids = set()
        if channels:
            missing = channels.filtered(lambda ch: not ch.saleor_channel_id)
            if missing:
                names = ", ".join(missing.mapped("display_name"))
                raise UserError(
                    _(
                        "Some channels on this product"
                        " are not synced to Saleor yet: %s.\n"
                        "Please sync these channels first.",
                        names,
                    )
                )
            desired_ids = {ch.saleor_channel_id for ch in channels}

        # Fetch current listings from Saleor
        self._refresh_token(client)
        current = client.product_channel_listings(saleor_product_id) or []
        current_ids = {
            item.get("channel", {}).get("id") for item in current if item.get("channel")
        }

        to_add_ids = sorted(list(desired_ids - current_ids))
        to_remove_ids = sorted(list(current_ids - desired_ids))

        update_channels = [
            {
                "channelId": ch_id,
                "isPublished": True,
                "isAvailableForPurchase": True,
                "visibleInListings": True,
            }
            for ch_id in to_add_ids
        ]

        if update_channels or to_remove_ids:
            client.product_channel_listing_update(
                saleor_product_id,
                update_channels=update_channels,
                remove_channels=to_remove_ids,
            )
        return True
