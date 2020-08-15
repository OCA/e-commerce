# Copyright 2020 Carlos Lopez Mite <carlos.lopez@odooerp.cl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models

from odoo.addons.phone_validation.tools import phone_validation


class PhoneValidationMixin(models.AbstractModel):
    _inherit = "phone.validation.mixin"

    def phone_format(self, number, country=None, company=None):
        # override function for change variable
        # raise_exception=True
        country = country or self._phone_get_country()
        if not country:
            return number
        always_international = (
            company.phone_international_format == "prefix"
            if company
            else self._phone_get_always_international()
        )
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            always_international=always_international,
            raise_exception=True,
        )
