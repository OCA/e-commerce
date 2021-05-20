# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    website_sale_checkout_skip_message = fields.Text(
        string="Website Sale SKip Message",
        required=True,
        default="Our team will check your order and send you payment information soon.",
    )
    checkout_skip_payment = fields.Boolean(compute="_compute_checkout_skip_payment")

    def _compute_checkout_skip_payment(self):
        for rec in self:
            rec.checkout_skip_payment = (
                request.env.user.partner_id.skip_website_checkout_payment
            )
