# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def get_website_sale_custom_filters(self, category=False):
        self.ensure_one()
        filter_obj = self.env["website.sale.custom.filter"]
        domain = [("website_ids", "=", self.id)]
        if category:
            domain.append(("website_category_ids", "=", category.id))
        filters = filter_obj.search(domain)
        return filters
