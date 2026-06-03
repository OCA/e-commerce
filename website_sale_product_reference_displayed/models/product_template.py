# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        """Render the search title from ``display_name`` instead of ``name``.

        This keeps the search results consistent with
        the rest of the shop and exposes the reference.

        The behaviour is toggleable per website, like the rest of the
        options, through the ``search_display_name`` view.
        """
        detail = super()._search_get_detail(website, order, options)
        if not (
            website
            and website.is_view_active(
                "website_sale_product_reference_displayed.search_display_name"
            )
        ):
            return detail
        fetch_fields = detail.get("fetch_fields", [])
        if "display_name" not in fetch_fields:
            fetch_fields.append("display_name")
        name_mapping = detail.get("mapping", {}).get("name")
        if name_mapping:
            name_mapping["name"] = "display_name"
        return detail
