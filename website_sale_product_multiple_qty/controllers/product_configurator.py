# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleProductConfiguratorMultipleController(
    WebsiteSaleProductConfiguratorController
):
    def _get_basic_product_information(
        self,
        product_or_template,
        pricelist,
        combination,
        quantity=None,
        uom=None,
        currency=None,
        date=None,
        **kwargs,
    ):
        product_info = super()._get_basic_product_information(
            product_or_template,
            pricelist,
            combination,
            quantity=quantity,
            uom=uom,
            currency=currency,
            date=date,
            **kwargs,
        )
        get_sale_multiple_vals = (
            self.env["product.template"]
            .with_context(product_configurator=True)
            ._get_sale_multiple_vals
        )
        product_info.update(get_sale_multiple_vals(product_or_template, uom))
        return product_info
