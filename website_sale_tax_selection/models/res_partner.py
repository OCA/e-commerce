# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    website_show_line_subtotals_tax_selection = fields.Selection(
        selection=[
            ("tax_excluded", "Tax Excluded"),
            ("tax_included", "Tax Included"),
        ],
        string="Website Tax Display",
        default="tax_excluded",
        help=(
            "Specify how product prices are displayed on the website for this "
            "commercial entity. Leave empty to use the website setting."
        ),
    )

    @api.model
    def _commercial_fields(self):
        """Add website tax display to commercial fields."""
        return super()._commercial_fields() + [
            "website_show_line_subtotals_tax_selection"
        ]

    def write(self, vals):
        result = super().write(vals)
        if "website_show_line_subtotals_tax_selection" in vals:
            # The website's non-stored compute reads this field through the
            # current request/env user's partner, a path `@api.depends` can't
            # express, so its cache is never auto-invalidated on this write.
            self.env["website"].invalidate_model(["show_line_subtotals_tax_selection"])
        return result
