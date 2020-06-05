# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.sale.controllers.variant import VariantController


class WebsiteSaleVariantController(VariantController):
    @http.route(
        ["/sale/get_combination_info_minimal_price"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_combination_info_minimal_price(self, product_template_ids, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """

        res = []
        templates = request.env["product.template"].sudo().browse(product_template_ids)
        for template in templates.filtered(lambda t: t.is_published):
            cheaper_variant = template.product_variant_ids.sorted(
                key=lambda p: p._get_combination_info_variant().get("price")
            )[:1]
            res.append(
                {
                    "id": template.id,
                    "price": cheaper_variant._get_combination_info_variant().get(
                        "price"
                    ),
                    "distinct_prices": self._compute_has_distinct_variant_price(
                        template
                    ),
                }
            )

        return res

    def _compute_has_distinct_variant_price(self, template):
        if template.product_variant_count > 1:
            prices = template.product_variant_ids.mapped("price")
            if len(prices) > 1:
                return True
        return False
