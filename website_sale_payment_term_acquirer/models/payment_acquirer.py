from odoo import fields, models


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"
    _order = "display_main_payment_term desc"

    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
    )
    display_main_payment_term = fields.Boolean(
        string="Display as partner's main payment term"
    )
