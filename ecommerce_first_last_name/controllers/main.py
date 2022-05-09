import logging

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSaleFirstLastname(WebsiteSale):
    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(
            WebsiteSaleFirstLastname, self
        ).checkout_form_validate(mode, all_form_values, data)
        if "name" in data and not data.get("name"):
            error["name"] = "missing"
        if "last_name" in data and not data.get("last_name"):
            error["last_name"] = "missing"
        if data.get("company_type", "") == "company" and not data.get("company_name"):
            error["company_name"] = "missing"

        return error, error_message

    def values_postprocess(self, order, mode, values, errors, error_msg):
        last_name = values.get("last_name")
        if last_name and values.get("name"):
            values["name"] = values.get("name") + " " + last_name
        elif last_name:
            values["name"] = last_name
        company_type = "person"
        new_values, errors, error_msg = super(
            WebsiteSaleFirstLastname, self
        ).values_postprocess(order, mode, values, errors, error_msg)
        if company_type:
            new_values["company_type"] = company_type
        if last_name:
            new_values["last_name"] = last_name
        return new_values, errors, error_msg
