# Copyright 2018 Denis Mudarisov (IT-Projects LLC)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class WebsiteSaleExtended(WebsiteSale):
    def values_preprocess(self, order, mode, values):
        return values

    def _get_mandatory_billing_fields(self):
        return [
            fname
            for fname in super()._get_mandatory_billing_fields()
            if fname != "name"
        ]

    def _get_mandatory_shipping_fields(self):
        return [
            fname
            for fname in super()._get_mandatory_billing_fields()
            if fname != "name"
        ]


class CustomerPortalExtend(CustomerPortal):

    MANDATORY_BILLING_FIELDS = [
        "firstname", "lastname", "phone",
        "email", "street", "city", "country_id"
    ]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]
