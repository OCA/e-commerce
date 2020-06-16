# Copyright 2020 ADHOC
from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        if self.detect_exceptions():
            website_draft = self.filtered(lambda o: o.state == "draft" and o.website_id)
            if website_draft:
                website_draft.action_quotation_sent()
        return super().action_confirm()
