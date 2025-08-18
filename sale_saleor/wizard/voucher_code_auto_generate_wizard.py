import uuid

from odoo import fields, models
from odoo.exceptions import UserError


class VoucherCodeGenerateWizard(models.TransientModel):
    _name = "voucher.code.generate.wizard"
    _description = "Generate Voucher Codes Wizard"

    code_quantity = fields.Integer(
        string="Code Quantity (max 50)",
        required=True,
    )
    code_prefix = fields.Char(
        help="If left empty, the code will be UUID only\n"
        " (e.g. a6db9870-f46c-44da-8097-21f318eae4a5)"
    )

    def action_confirm_generate(self):
        """Generate multiple voucher codes for the active voucher."""
        self.ensure_one()
        if self.code_quantity <= 0 or self.code_quantity > 50:
            raise UserError(self.env._("Code Quantity must be between 1 and 50."))

        active_id = self.env.context.get("active_id")
        voucher = self.env["saleor.voucher"].browse(active_id)
        if not voucher:
            raise UserError(self.env._("No active voucher found."))

        codes = []
        prefix = (self.code_prefix or "").strip()

        for _ in range(self.code_quantity):
            uuid_str = str(uuid.uuid4())
            code = f"{prefix}-{uuid_str}" if prefix else uuid_str
            codes.append(
                {
                    "voucher_id": voucher.id,
                    "code": code,
                    "status": "draft",
                }
            )

        # Create child records directly to avoid triggering a write on the voucher
        self.env["saleor.voucher.code"].create(codes)
        return {"type": "ir.actions.act_window_close"}
