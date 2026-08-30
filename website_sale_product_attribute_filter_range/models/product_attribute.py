# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    display_type = fields.Selection(
        selection_add=[("range", "Range Slider")],
        ondelete={"range": "set default"},
    )
    website_range_step = fields.Float(
        string="Range Step",
        digits=(12, 2),
        default=0.5,
        help="Step increment for the range slider on the website shop. "
        "For example, 0.5 allows selecting 80.0, 80.5, 81.0, etc. "
        "Use 1 for integer steps.",
    )

    _sql_constraints = [
        (
            "check_range_no_variant",
            "CHECK(display_type != 'range' OR create_variant = 'no_variant')",
            "Range slider display type is not compatible with"
            " the creation of variants.",
        ),
    ]

    @api.onchange("display_type")
    def _onchange_display_type_range(self):
        if self.display_type == "range":
            self.create_variant = "no_variant"
