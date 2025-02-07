from odoo import http

from odoo.addons.website.controllers import main

from .website_sale import WebsiteSale


class Website(main.Website):
    @http.route()
    def autocomplete(
        self,
        options=None,
        **kwargs,
    ):
        (
            allowed_product_ids,
            assortment_restriction,
        ) = WebsiteSale()._get_products_allowed()
        if assortment_restriction:
            options["allowed_product_domain"] = [
                ("product_variant_ids", "in", list(allowed_product_ids))
            ]
        return super().autocomplete(
            options=options,
            **kwargs,
        )
