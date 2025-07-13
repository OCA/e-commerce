# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request


class PublicReviewStats(http.Controller):
    @http.route(
        "/customer_review/product_template/stats/<int:res_id>",
        type="json",
        auth="public",
        website=True,
    )
    def get_review_stats(self, res_id):
        # Make the call with sudo to bypass access rights for public users
        model = "product.template"
        record = request.env[model].sudo().browse(res_id)
        result = record.rating_get_stats()
        return result
