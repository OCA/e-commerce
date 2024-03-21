# Copyright 2018 Denis Mudarisov (IT-Projects LLC)
# Copyright 2023 Alessandro Uffreduzzi (PyTech SRL)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleFirstname(WebsiteSale):
    def _get_mandatory_fields_billing(self, country_id=False):
        req = super()._get_mandatory_fields_billing(country_id)
        req = ["firstname", "lastname"] + [field for field in req if field != "name"]
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = super()._get_mandatory_fields_shipping(country_id)
        req = ["firstname", "lastname"] + [field for field in req if field != "name"]
        return req

    def _checkout_form_save(self, mode, checkout, all_values):
        # Do not save the name if firstname and lastname are present
        # It will be computed automatically
        if "name" in checkout and "firstname" in checkout and "lastname" in checkout:
            del checkout["name"]
        return super()._checkout_form_save(mode, checkout, all_values)

    @http.route()
    def address(self, **kw):
        if "submitted" in kw and request.httprequest.method == "POST":
            # Compute the name to hook into all the logic already in Odoo
            # concerning the name field
            if not kw.get("name") and ("firstname" in kw or "lastname" in kw):
                kw["name"] = request.env["res.partner"]._get_computed_name(
                    lastname=kw.get("lastname"), firstname=kw.get("firstname")
                )

        return super().address(**kw)
