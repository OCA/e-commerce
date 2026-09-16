# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductDocument(models.Model):
    _inherit = "product.document"

    @api.constrains("res_model", "shown_on_product_page")
    def _unsupported_product_product_document_on_ecommerce(self):
        # Full override: this module makes the product page variant-aware,
        # so the base method's blanket rejection of product.product
        # documents no longer applies.
        # Full override because the base loop unconditionally raises for that case.
        return
