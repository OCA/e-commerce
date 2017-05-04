# -*- coding: utf-8 -*-
# Copyright 2015 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.website_sale.controllers.main import website_sale


class WebsiteSale(website_sale):
    def _get_mandatory_billing_fields(self):
        result = super(WebsiteSale, self)._get_mandatory_billing_fields()
        result.append("vat")
        return result

    def _get_optional_billing_fields(self):
        result = super(WebsiteSale, self)._get_optional_billing_fields()
        try:
            result.remove("vat")
        except ValueError:  # pragma: no-cover
            # If any other addon removed it already, do not die
            pass
        return result
