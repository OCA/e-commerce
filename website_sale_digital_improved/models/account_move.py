# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _website_sale_digital_get_attachments(self):
        """
        Return attachment records for products that are considered digital products
        """
        return self.env["ir.attachment"].search(
            [
                "|",
                "&",
                ("res_model", "=", "product.template"),
                ("res_id", "in", self.invoice_line_ids.product_id.product_tmpl_id.ids),
                "&",
                ("res_model", "=", "product.product"),
                ("res_id", "in", self.invoice_line_ids.product_id.ids),
                ("product_downloadable", "=", True),
                ("product_mailable", "=", True),
            ]
        )

    def _message_set_main_attachment_id(self, attachment_ids):
        # never use a digital product as main attachment
        Attachment = self.env["ir.attachment"]
        attachment_ids = [
            attachment_tuple
            for attachment_tuple in attachment_ids
            if attachment_tuple[0] != fields.Command.LINK
            or not Attachment.browse(attachment_tuple[1]).product_downloadable
        ]
        return super()._message_set_main_attachment_id(attachment_ids)
