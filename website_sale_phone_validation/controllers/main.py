# Copyright 2020 Carlos Lopez Mite <carlos.lopez@odooerp.cl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import tools
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_phone_fields_to_validate_sale(self):
        return ["phone", "mobile"]

    def checkout_form_validate(self, mode, all_form_values, data):
        phone_validation_model = request.env["phone.validation.mixin"].sudo()
        error, error_message = super(WebsiteSale, self).checkout_form_validate(
            mode, all_form_values, data
        )
        for field_name in self._get_phone_fields_to_validate_sale():
            if not data.get(field_name):
                continue
            try:
                data.update(
                    {
                        field_name: phone_validation_model.phone_format(
                            data.get(field_name)
                        )
                    }
                )
            except Exception as ex:
                error[field_name] = "error"
                error_message.append(tools.ustr(ex))
        return error, error_message
