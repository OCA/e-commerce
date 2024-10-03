# Copyright 2024 Studio73 - Ferran Mora
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _trigram_enumerate_words(self, search_details, search, limit):
        final_search_details = []
        for detail in search_details:
            if detail.get("model", "") == "product.template":
                search_fields = detail.get("search_fields", [])
                if search_fields:
                    search_fields.remove("barcode")
                    detail["search_fields"] = search_fields
            final_search_details.append(detail)
        return super()._trigram_enumerate_words(final_search_details, search, limit)
