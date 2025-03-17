from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _get_products_alternative_products(self, *args):
        products = super()._get_products_alternative_products(*args)
        if not products:
            return products
        restricted_products_dict = self.env[
            "product.template"
        ].get_product_assortment_restriction_info(products.ids)
        if not restricted_products_dict:
            return products
        return products.filtered(
            lambda p: p.id not in restricted_products_dict
            or not any(
                assortment.website_availability == "no_show"
                for assortment in restricted_products_dict[p.id]
            )
        )
