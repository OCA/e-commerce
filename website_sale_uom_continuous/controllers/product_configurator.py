# Copyright 2026 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleUomContinuousProductConfiguratorController(
    WebsiteSaleProductConfiguratorController
):
    def _handle_uom_continuous_quantity(self, kwargs):
        """Set the quantity in ``kwargs`` to one allowed by its UoM."""
        if kwargs.get("quantity") and kwargs.get("product_template_id"):
            uom = (
                kwargs.get("product_uom_id")
                and request.env["uom.uom"].browse(kwargs["product_uom_id"])
            ) or self._get_product_template(kwargs["product_template_id"]).uom_id
            quantity = kwargs["quantity"]
            kwargs["quantity"] = (
                uom.round(float(quantity)) if uom._is_continuous() else int(quantity)
            )

    @route(type="jsonrpc")
    def website_sale_product_configurator_get_values(self, *args, **kwargs):
        # OVERRIDE: open the configurator with a quantity allowed by the UoM.
        self._handle_uom_continuous_quantity(kwargs)
        return super().website_sale_product_configurator_get_values(*args, **kwargs)

    @route(type="jsonrpc")
    def website_sale_product_configurator_update_combination(self, *args, **kwargs):
        # OVERRIDE: price the quantity allowed by the UoM, e.g. when switching to a
        # UoM that is not continuous.
        self._handle_uom_continuous_quantity(kwargs)
        return super().website_sale_product_configurator_update_combination(
            *args, **kwargs
        )

    def _get_product_information(self, product_template, *args, **kwargs):
        # OVERRIDE: let the configurator only allow decimal quantities for
        # continuous UoMs.
        values = super()._get_product_information(product_template, *args, **kwargs)
        for uom_values in [values["uom"], *values.get("available_uoms", [])]:
            uom_values["is_continuous"] = (
                request.env["uom.uom"].browse(uom_values["id"])._is_continuous()
            )
        return values
