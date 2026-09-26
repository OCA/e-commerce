# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import http


class WebsiteSaleViesPopulator(http.Controller):
    @http.route(
        "/website_sale_vies_populator/get_vies_data",
        type="json",
        auth="public",
        methods=["POST"],
    )
    def check_vies(self, vat):
        return dict(http.request.env["res.partner"]._get_vies_data(vat))
