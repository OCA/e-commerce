# Copyright 2022 Studio73 - Miguel Gandia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleSearchByBarcode(WebsiteSale):
    def _get_search_domain(
        self, search, category, attrib_values, search_in_description=True
    ):
        domains = super()._get_search_domain(
            search, category, attrib_values, search_in_description
        )
        _domains = []
        if search:
            for srch in search.split(" "):
                subdomains = [("barcode", "=", srch)]
                _domains = expression.OR([_domains, subdomains])
        return expression.OR([domains, _domains])
