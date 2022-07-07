# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_under_validation_exceptions(self):
        res = super(SaleOrder, self)._get_under_validation_exceptions()
        res.extend(
            [
                "signed_by",
                "signed_on",
                "signature",
                "reference",
                "message_main_attachment_id",
            ]
        )
        return res

    def request_validation(self):
        if self.env.context.get("send_email_customer"):
            subtypes = self.env.ref(
                "sale_tier_validation.sale_order_tier_validation_requested"
            )
            subtypes += self.env.ref(
                "sale_tier_validation.sale_order_tier_validation_accepted"
            )
            subtypes += self.env.ref(
                "sale_tier_validation.sale_order_tier_validation_rejected"
            )
            for order in self:
                # order.message_post_with_template(
                #     template_id.id,
                #     composition_mode="comment",
                #     email_layout_xmlid=(
                #     "website_sale_tier_validation.mail_notification_tier_validation"
                #     ),
                # )
                order.message_subscribe(
                    partner_ids=order.partner_id.ids, subtype_ids=subtypes.ids
                )
                order.sudo().state = "sent"
        return super().request_validation()
