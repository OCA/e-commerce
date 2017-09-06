# -*- coding: utf-8 -*-
# Copyright 2015-2017 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.http import request
from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _get_mandatory_billing_fields(self):
        result = super(WebsiteSale, self)._get_mandatory_billing_fields()
        return result + self._mandatory_legal_terms()

    def _get_mandatory_shipping_fields(self):
        result = super(WebsiteSale, self)._get_mandatory_shipping_fields()
        return result + self._mandatory_legal_terms()

    def _mandatory_legal_terms(self):
        """Require ``accepted_legal_terms`` only if we are validating."""
        result = []
        if request.context.get("needs_legal"):
            result.append("accepted_legal_terms")
        return result

    def checkout_form_validate(self, mode, all_form_values, data):
        """Require accepting legal terms to validate form."""
        # Patch context
        old_context = request.context
        new_context = dict(request.context, needs_legal=True)
        request.context = new_context
        result = super(WebsiteSale, self).checkout_form_validate(
            mode, all_form_values, data)
        # Unpatch context
        request.context = old_context
        return result
