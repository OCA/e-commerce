# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    # OVERRIDE: make the tax display dynamic so the current website partner can
    # specify a value that takes precedence over the standard website behavior.
    show_line_subtotals_tax_selection = fields.Selection(
        store=False,
    )

    @api.depends("company_id.account_fiscal_country_id")
    @api.depends_context("uid")
    def _compute_show_line_subtotals_tax_selection(self):
        # OVERRIDE: apply the current website partner tax display preference,
        # when set, on top of the standard website behavior.
        partner = self._get_current_website_tax_selection_partner()
        if partner_tax_selection := partner.website_show_line_subtotals_tax_selection:
            for website in self:
                website.show_line_subtotals_tax_selection = partner_tax_selection
        else:
            return super()._compute_show_line_subtotals_tax_selection()

    def _get_current_website_tax_selection_partner(self):
        """Return the partner used to resolve website tax display preference.

        :return: Current HTTP request user partner, or environment user partner
            when running outside an HTTP request.
        :rtype: res.partner
        """
        if request and request.env:
            return request.env.user.partner_id
        return self.env.user.partner_id
