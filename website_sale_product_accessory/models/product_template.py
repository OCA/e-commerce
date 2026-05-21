# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_page_accessory_products(self):
        """Return accessory variants suitable for display on the product page.

        Filters mirror ``SaleOrder._cart_accessories`` so the product page
        surfaces the same set of accessories as the cart would, minus the
        cart-specific exclusions (current cart contents and parent variant
        combination). The ``_website_show_quick_add`` logic is inlined to
        avoid depending on a bound HTTP request, since this helper can be
        called from contexts other than a website request.
        """
        self.ensure_one()
        website = self.env["website"].get_current_website()
        prevent_zero_price = website.prevent_zero_price_sale
        accessory_products = self._get_website_accessory_product()
        product_domain = self.env["website"]._product_domain()
        company_domain = self.env["product.product"]._check_company_domain(
            self.company_id or website.company_id
        )
        return accessory_products.filtered(
            lambda product: (
                product.product_tmpl_id != self
                and product.filtered_domain(product_domain)
                and product.filtered_domain(company_domain)
                and (not prevent_zero_price or product._get_contextual_price())
            )
        )
