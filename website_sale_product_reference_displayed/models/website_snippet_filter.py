from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _get_products_latest_sold(self, website, limit, domain, **kwargs):
        products = super()._get_products_latest_sold(website, limit, domain, **kwargs)
        if products:
            return products.with_context(display_default_code=True)
        else:
            return products

    def _get_products_latest_viewed(self, website, limit, domain, **kwargs):
        products = super()._get_products_latest_viewed(website, limit, domain, **kwargs)
        if products:
            return products.with_context(display_default_code=True)
        else:
            return products

    def _get_products_recently_sold_with(
        self, website, limit, domain, product_template_id, **kwargs
    ):
        products = super()._get_products_recently_sold_with(
            website, limit, domain, product_template_id, **kwargs
        )
        if products:
            return products.with_context(display_default_code=True)
        else:
            return products

    def _get_products_accessories(
        self, website, limit, domain, product_template_id=None, **kwargs
    ):
        products = super()._get_products_accessories(
            website, limit, domain, product_template_id=product_template_id, **kwargs
        )
        if products:
            return products.with_context(display_default_code=True)
        else:
            return products

    def _get_products_alternative_products(
        self, website, limit, domain, product_template_id=None, **kwargs
    ):
        products = super()._get_products_alternative_products(
            website, limit, domain, product_template_id=product_template_id, **kwargs
        )
        if products:
            return products.with_context(display_default_code=True)
        else:
            return products
