# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.website_sale_comparison.controllers.main import (
    WebsiteSaleProductComparison,
)


class WebsiteSaleComparisonHidePrice(WebsiteSaleProductComparison):
    @route()
    def get_product_data(self, product_ids):
        product_data = super().get_product_data(product_ids)
        website = request.website
        products = request.env["product.product"].search([("id", "in", product_ids)])
        products_by_id = {p.id: p for p in products}
        for item in product_data:
            product = products_by_id.get(item["id"])
            item["website_hide_price"] = bool(
                not website.website_show_price
                or (product and product.website_hide_price)
            )
        return product_data
