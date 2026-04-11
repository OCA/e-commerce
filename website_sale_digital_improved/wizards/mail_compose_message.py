# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _onchange_template_id(self, template_id, composition_mode, model, res_id):
        # add digital products if configured accordingly and we're sending the invoice
        # template
        result = super()._onchange_template_id(
            template_id, composition_mode, model, res_id
        )
        if model == "account.move" and composition_mode == "comment":
            invoice_mail_template_id = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("sale.default_invoice_email_template")
            )
            if str(template_id) == invoice_mail_template_id:
                invoice = (
                    self.env[model]
                    .browse(res_id)
                    .filtered(lambda x: x.payment_state == "paid")
                )
                if invoice:
                    digital_products = invoice._website_sale_digital_get_attachments()
                    if digital_products:
                        attachment_ids = result["value"].setdefault(
                            "attachment_ids", []
                        )
                        attachment_ids.extend(
                            map(fields.Command.link, digital_products.ids)
                        )
        return result
