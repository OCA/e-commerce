# Copyright 2023 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleVariantControllerMatomo(WebsiteSaleVariantController):
    @http.route()
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, **kw
    ):
        """Adapts the route to adapt get_combination_info for Matomo analytics."""
        combination = super().get_combination_info_website(
            product_template_id, product_id, combination, add_qty, **kw
        )
        website = request.website
        if (
            "product_tracking_info" not in combination
            and website.has_matomo_analytics
            and website.matomo_analytics_host
        ):
            combination["product_tracking_info"] = request.env[
                "product.template"
            ].get_google_analytics_data(combination)

        return combination
