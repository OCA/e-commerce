# Copyright 2015 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_mandatory_fields_billing(self, country_id=False):
        result = super()._get_mandatory_fields_billing(country_id)
        result.append("vat")
        return result
