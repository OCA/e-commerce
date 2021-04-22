# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.http import request, route

from ...website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def checkout_redirection(self, order):
        """Send to survey if pending."""
        pending_survey_lines = order._lines_pending_survey()
        if pending_survey_lines:
            return request.redirect(pending_survey_lines[0]._survey_url())
        return super().checkout_redirection(order)
