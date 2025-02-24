# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        res = super()._search_get_detail(website, order, options)
        domain = res["base_domain"]
        brand_id = options.get("brand")
        if brand_id:
            domain.append([("product_brand_id", "=", brand_id)])
        res["base_domain"] = domain
        return res
