# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_skip_payment_quotation = fields.Boolean(
        # Set on orders that completed the website checkout via the
        # skip-payment flow. These quotations must not be resurrected as the
        # customer's cart on subsequent visits, otherwise the website would
        # keep showing the items the customer already "ordered".
        string="Skip-Payment Quotation",
        copy=False,
        readonly=True,
        index=True,
    )
