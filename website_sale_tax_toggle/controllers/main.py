# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleTaxToggle(WebsiteSale):
    @http.route(["/website/tax_toggle"], type="json", auth="public", website=True)
    def tax_toggle(self):
        if request.session.get("tax_toggle_taxed") is None:
            tax_toggle_preactivated = request.website.tax_toggle_preactivated
            request.session["tax_toggle_taxed"] = tax_toggle_preactivated
        request.session["tax_toggle_taxed"] = not request.session["tax_toggle_taxed"]
        return request.session["tax_toggle_taxed"]
