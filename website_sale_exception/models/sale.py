# Copyright 2020 ADHOC
from odoo import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        if self.detect_exceptions():
            website_draft = self.filtered(lambda o: o.state == 'draft' and o.website_id)
            if website_draft:
                website_draft.force_quotation_send()
        return super().action_confirm()
