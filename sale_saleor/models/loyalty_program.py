# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models
from odoo.exceptions import UserError

from ..helpers import get_active_saleor_account, html_to_editorjs, to_saleor_datetime


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

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
                "saleor": self.env._("Sale Orders"),
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
                self.env._("Only programs with type 'Saleor Discount' can be synced.")
            )
        account = get_active_saleor_account(self.env, raise_if_missing=True)
        if len(programs) == 1:
            prog = programs
            payload = prog._saleor_prepare_promotion_payload()
            account.job_promotion_sync(prog.id, payload)
            queued = False
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
            queued = True
        # Notify via client action
        msg = self.env._(
            "Queued sync of %s promotion(s) to Saleor.",
            len(programs)
            if queued
            else self.env._(
                "Triggered sync of %s promotion(s) to Saleor.", len(programs)
            ),
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Saleor Promotion Sync"),
                "message": msg,
                "type": "success",
                "sticky": False,
            },
        }
