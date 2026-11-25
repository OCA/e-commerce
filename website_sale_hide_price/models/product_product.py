# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _is_add_to_cart_allowed(self):
        return (
            super()._is_add_to_cart_allowed()
            and not self.product_tmpl_id._website_hide_price_blocks_cart()
        )

    def _website_show_quick_add(self):
        # Suggested accessories in the cart and quick add would offer a
        # product that cannot be added to the cart
        return (
            super()._website_show_quick_add()
            and not self.product_tmpl_id._website_hide_price_blocks_cart()
        )

    def _to_markup_data(self, website):
        markup_data = super()._to_markup_data(website)
        offers = markup_data.get("offers")
        if offers and self.product_tmpl_id._website_price_hidden():
            # Keep the offer, other modules extend it (e.g. availability)
            offers.pop("price", None)
            offers.pop("priceCurrency", None)
        return markup_data
