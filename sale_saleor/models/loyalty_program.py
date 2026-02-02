# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, fields, models
from odoo.exceptions import UserError

from ..helpers import (
    get_active_saleor_account,
    html_to_editorjs,
    make_link,
    to_saleor_datetime,
)


class LoyaltyProgram(models.Model):
    _name = "loyalty.program"
    _inherit = ["loyalty.program", "mail.thread", "mail.activity.mixin"]

    program_type = fields.Selection(
        selection_add=[
            ("saleor", "Saleor Discount"),
        ],
        ondelete={"saleor": "cascade"},
    )
    discount_type = fields.Selection(
        selection=[("catalogue", "Catalog"), ("order", "Order")],
        required=True,
        default="catalogue",
    )
    saleor_description = fields.Html(string="Saleor Description (HTML)")
    set_end_date = fields.Boolean()
    active_date_from = fields.Datetime(string="Start Date (Saleor)")
    active_date_to = fields.Datetime(string="End Date (Saleor)")
    discount_rule_ids = fields.One2many("discount.rule", "program_id", string="Rules")
    saleor_promotion_id = fields.Char(
        string="Saleor Promotion ID",
        copy=False,
        index=True,
        help="ID of this promotion in Saleor",
    )

    def _program_items_name(self):
        res = super()._program_items_name()
        res.update(
            {
                "saleor": _("Sale Orders"),
            }
        )
        return res

    def _saleor_prepare_promotion_payload(self):
        self.ensure_one()
        # Minimal payload to avoid schema mismatches across Saleor versions
        # Map Odoo discount_type to Saleor PromotionTypeEnum
        type_map = {
            "catalogue": "CATALOGUE",
            "order": "ORDER",
        }
        saleor_type = type_map.get(self.discount_type)
        payload = {
            "name": self.name,
            "type": saleor_type,
        }
        if self.saleor_description:
            # Convert HTML to EditorJS
            desc = html_to_editorjs(self.saleor_description)
            if desc is not None:
                # Saleor expects JSONString
                payload["description"] = desc
        # Optional: include dates if present; field names may vary by Saleor version
        if self.active_date_from:
            payload["startDate"] = to_saleor_datetime(self.active_date_from)
        if self.set_end_date and self.active_date_to:
            payload["endDate"] = to_saleor_datetime(self.active_date_to)
        return payload

    def action_saleor_sync(self):
        programs = self.filtered(lambda p: p.program_type == "saleor")
        if not programs:
            raise UserError(
                _("Only programs with type 'Saleor Discount' can be synced.")
            )
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(programs) == 1:
            prog = programs
            payload = prog._saleor_prepare_promotion_payload()
            account.job_promotion_sync(prog.id, payload)
        else:
            batch_size = getattr(account, "job_batch_size", 10) or 10
            items = []
            for prog in programs:
                payload = prog._saleor_prepare_promotion_payload()
                items.append({"id": prog.id, "payload": payload})
            for i in range(0, len(items), batch_size):
                chunk = items[i : i + batch_size]
                if hasattr(account, "with_delay"):
                    account.with_delay().job_promotion_sync_batch(chunk)
                else:
                    account.job_promotion_sync_batch(chunk)
        # Log detailed message per program, similar to other Saleor objects
        base = (account.base_url or "").rstrip("/")
        for prog in programs:
            dash_url = ""
            if base and prog.saleor_promotion_id:
                dash_url = (
                    f"{base}/dashboard/discounts/sales/{prog.saleor_promotion_id}"
                )

            link_html = (
                f"<li><b>Saleor</b>: {make_link('View in Saleor', dash_url)}</li>"
                if dash_url
                else ""
            )

            body = (
                "<p><b>Synced promotion to Saleor</b></p>"
                "<ul>"
                f"<li><b>Account</b>: {account.email or account.name}</li>"
                f"<li><b>Program</b>: {prog.display_name}</li>"
                f"<li><b>Saleor Promotion ID</b>: {prog.saleor_promotion_id or ''}</li>"
                f"{link_html}"
                "</ul>"
            )
            prog.message_post(body=body)

        return True
