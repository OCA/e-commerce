# Copyright 2022 Studio73 - Miguel Gandia
# Copyright 2024 Studio73 - Sergi Biosca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _search_get_detail(self, website, order, options):
        res = super()._search_get_detail(website, order, options)
        res["search_fields"].append("barcode")
        return res
