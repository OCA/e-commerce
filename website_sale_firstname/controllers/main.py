# Copyright 2018 Denis Mudarisov (IT-Projects LLC)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExtended(WebsiteSale):
    def _get_mandatory_billing_fields(self):
        return [
            fname for fname in super()._get_mandatory_billing_fields()
            if fname != 'name'
        ]

    def _get_mandatory_shipping_fields(self):
        return [
            fname for fname in super()._get_mandatory_billing_fields()
            if fname != 'name'
        ]
