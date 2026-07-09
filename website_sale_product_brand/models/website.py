# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    brand_filter_display_mode = fields.Selection(
        selection=[
            ("list", "Full list"),
            ("limited", "Limited list"),
            ("letters", "Alphabetical accordion"),
        ],
        default="list",
        required=True,
        help="Controls how brands are displayed in the shop filter: "
        "'Full list' shows all brands, 'Limited list' shows the first 5 brands "
        "with an option to load more using 'Show more', and 'Alphabetical accordion' "
        "groups brands by letter when there are more than 50 brands.",
    )

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if not self.has_ecommerce_access():
            return result
        if search_type in ["products", "all"]:
            result.append(
                self.env["product.brand"]._search_get_detail(self, order, options)
            )
        return result
