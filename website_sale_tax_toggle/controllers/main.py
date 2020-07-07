# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleTaxToggle(WebsiteSale):

    @http.route(
        ['/website/tax_toggle'], type='json', auth="public", website=True)
    def tax_toggle(self):
        # Create a session variable
        request.session['tax_toggle_taxed'] = not request.session.get(
            'tax_toggle_taxed', False)
        return request.session['tax_toggle_taxed']
