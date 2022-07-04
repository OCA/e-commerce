# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.http import request

from odoo.addons.sale.controllers.variant import VariantController


class WebsiteSaleVariantController(VariantController):
    @http.route(
        ["/sale/get_info_assortment_preview"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_info_assortment_preview(self, product_template_ids, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        res = []
        templates = request.env["product.template"].sudo().browse(product_template_ids)
        not_allowed_product_dict = templates.get_product_assortment_restriction_info(
            templates.mapped("product_variant_ids.id")
        )
        for template in templates:
            variant_ids = set(template.product_variant_ids.ids)
            if (
                variant_ids
                and variant_ids & set(not_allowed_product_dict.keys()) == variant_ids
            ):
                res.append(
                    {
                        "id": template.id,
                        "message_unavailable": not_allowed_product_dict[
                            variant_ids.pop()
                        ][0].message_unavailable
                        or _("Not available"),
                    }
                )
        return res
