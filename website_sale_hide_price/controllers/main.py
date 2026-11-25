# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.http import request, route

from odoo.addons.website_sale.controllers.combo_configurator import (
    WebsiteSaleComboConfiguratorController,
)
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


def _product_template(product_or_template):
    if product_or_template._name == "product.template":
        return product_or_template
    return product_or_template.product_tmpl_id


def _check_configurator_allowed(product_template_id):
    """The configurators are part of the add to cart flow and return prices."""
    if not product_template_id:
        return
    template = request.env["product.template"].browse(int(product_template_id)).exists()
    if template and template._website_hide_price_blocks_cart():
        raise AccessError(request.env._("This product cannot be added to the cart."))


class WebsiteSaleHidePrice(WebsiteSale):
    @route()
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        tags="",
        **post,
    ):
        # Filtering or sorting by price would reveal the hidden prices
        if not request.website.website_show_price:
            min_price = max_price = 0.0
            if (post.get("order") or "").startswith("list_price"):
                post.pop("order")
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            tags=tags,
            **post,
        )


class WebsiteSaleHidePriceVariant(WebsiteSaleVariantController):
    @route()
    def get_combination_info_website(self, *args, **kwargs):
        combination_info = super().get_combination_info_website(*args, **kwargs)
        template = request.env["product.template"].browse(
            combination_info["product_template_id"]
        )
        return template._website_hide_price_combination_info(combination_info)


class WebsiteSaleHidePriceProductConfigurator(WebsiteSaleProductConfiguratorController):
    @route()
    def website_sale_product_configurator_get_values(self, *args, **kwargs):
        _check_configurator_allowed(kwargs.get("product_template_id"))
        return super().website_sale_product_configurator_get_values(*args, **kwargs)

    @route()
    def website_sale_product_configurator_update_combination(self, *args, **kwargs):
        _check_configurator_allowed(kwargs.get("product_template_id"))
        return super().website_sale_product_configurator_update_combination(
            *args, **kwargs
        )

    @route()
    def website_sale_product_configurator_get_optional_products(self, *args, **kwargs):
        _check_configurator_allowed(kwargs.get("product_template_id"))
        return super().website_sale_product_configurator_get_optional_products(
            *args, **kwargs
        )

    def _get_basic_product_information(
        self, product_or_template, pricelist, combination, **kwargs
    ):
        # Also covers the optional products, whose price can be hidden while
        # the main product's price is shown
        info = super()._get_basic_product_information(
            product_or_template, pricelist, combination, **kwargs
        )
        if _product_template(product_or_template)._website_price_hidden():
            info["price"] = 0.0
            info.pop("strikethrough_price", None)
        return info

    def _get_ptav_price_extra(self, ptav, currency, date, product_or_template):
        if _product_template(product_or_template)._website_price_hidden():
            return 0.0
        return super()._get_ptav_price_extra(ptav, currency, date, product_or_template)


class WebsiteSaleHidePriceComboConfigurator(WebsiteSaleComboConfiguratorController):
    @route()
    def website_sale_combo_configurator_get_data(self, *args, **kwargs):
        _check_configurator_allowed(kwargs.get("product_tmpl_id"))
        return super().website_sale_combo_configurator_get_data(*args, **kwargs)

    @route()
    def website_sale_combo_configurator_get_price(self, *args, **kwargs):
        _check_configurator_allowed(kwargs.get("product_tmpl_id"))
        return super().website_sale_combo_configurator_get_price(*args, **kwargs)
