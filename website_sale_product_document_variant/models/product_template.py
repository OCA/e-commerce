# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_variant_documents(self, variant):
        """Return the published documents for this template combined with
        `variant`'s own published documents (`variant` may be empty).
        """
        self.ensure_one()
        documents = self.sudo().product_document_ids.filtered(
            lambda doc: doc.shown_on_product_page
        )
        if variant:
            documents |= variant.sudo().product_document_ids.filtered(
                lambda doc: doc.shown_on_product_page
            )
        return documents

    def _get_variant_documents_html(self, variant):
        """Render the documents section content for `variant` (a
        `product.product` recordset, possibly empty), so it can be
        refreshed client-side when the customer changes variant.

        Always renders (returns an empty section rather than `None` when
        there is nothing to show) so the front-end can also hide the
        section on refresh, not just skip updating it.

        Called only from the `/website_sale/get_combination_info` controller.
        """
        self.ensure_one()
        documents = self._get_variant_documents(variant)
        return self.env["ir.qweb"]._render(
            "website_sale_product_document_variant.product_documents_content",
            {"product": self, "product_documents": documents},
        )
