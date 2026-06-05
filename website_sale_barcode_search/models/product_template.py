# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.fields import Domain


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_fetch(self, search_detail, search, limit, order):
        records, count = super()._search_fetch(search_detail, search, limit, order)
        base_domain = search_detail.get("base_domain")
        base_domain.append([("barcode", "ilike", search)])
        domain = Domain.AND(base_domain)
        tmpl_ids = self.search(domain)
        if tmpl_ids:
            records |= tmpl_ids
            count = len(records)
        return records, count
