from odoo import _, fields, models
from odoo.exceptions import UserError


class VoucherCodeManualWizard(models.TransientModel):
    _name = "voucher.code.manual.wizard"
    _description = "Manual Voucher Code Wizard"

    manual_code = fields.Char(
        string="Enter code", required=True, help="Manually enter a voucher code."
    )

    def action_confirm_manual(self):
        """Add the entered voucher code to the current voucher."""
        self.ensure_one()
        active_id = self.env.context.get("active_id")
        voucher = self.env["saleor.voucher"].browse(active_id)

        if not voucher:
            raise UserError(_("No active voucher found."))

        code_str = (self.manual_code or "").strip()
        if voucher.voucher_code_ids.filtered(lambda c: c.code == code_str):
            raise UserError(_("This code already exists."))

        self.env["saleor.voucher.code"].create(
            {
                "voucher_id": voucher.id,
                "code": code_str,
                "status": "draft",
            }
        )

        return {"type": "ir.actions.act_window_close"}
