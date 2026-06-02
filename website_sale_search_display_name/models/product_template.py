# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        """Render the search title from ``display_name`` instead of ``name``.

        The website search (autocomplete dropdown and ``/website/search`` page)
        renders the product title from the ``name`` field, whereas the rest of
        the eCommerce (shop grid, product page) relies on ``display_name``,
        which prepends the internal reference (``default_code``) when the
        ``display_default_code`` context flag is set. This keeps the search
        results consistent with the rest of the shop and exposes the reference.
        """
        detail = super()._search_get_detail(website, order, options)
        fetch_fields = detail.get("fetch_fields", [])
        if "display_name" not in fetch_fields:
            fetch_fields.append("display_name")
        name_mapping = detail.get("mapping", {}).get("name")
        if name_mapping:
            name_mapping["name"] = "display_name"
        return detail
