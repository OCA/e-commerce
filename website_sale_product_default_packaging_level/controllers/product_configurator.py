# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.sale_product_default_packaging_level.controllers.product_configurator import (  # noqa: E501
    SaleProductConfiguratorPackagingController,
)
from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)


class WebsiteSaleProductConfiguratorPackagingController(
    WebsiteSaleProductConfiguratorController, SaleProductConfiguratorPackagingController
):
    pass
