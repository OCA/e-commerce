# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _get_products(self, mode, **kwargs):
        # Dynamic product snippets build their base product domain through
        # website.website_domain(). Enable the existing multi-website domain
        # context here so snippets also consider products assigned through
        # website_ids, not only the main website_id.
        return super(
            WebsiteSnippetFilter,
            self.with_context(multi_website_domain=True),
        )._get_products(mode, **kwargs)

    def _filter_records_to_values(self, records, **options):
        # The multi_website_domain context is only needed while building the
        # product search domain. After products are found, Odoo computes their
        # website values and renders templates; during that phase
        # website.website_domain() may be called for non-product models such as
        # ir.ui.view. Clear the context from the product records to avoid
        # applying product-specific website_ids domains outside product searches.
        return super()._filter_records_to_values(
            records.with_context(multi_website_domain=False),
            **options,
        )
