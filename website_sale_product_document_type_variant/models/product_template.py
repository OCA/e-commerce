# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_variant_documents_html(self, variant):
        # Full override: renders the same combined document set (inherited
        # _get_variant_documents) through the grouped-by-type template
        # instead of website_sale_product_document_variant's plain list,
        # so an AJAX refresh doesn't undo website_sale_product_document_type's
        # grouping.
        self.ensure_one()
        documents = self._get_variant_documents(variant)
        return self.env["ir.qweb"]._render(
            "website_sale_product_document_type_variant"
            ".product_documents_content_by_type",
            {"product": self, "product_documents": documents},
        )
