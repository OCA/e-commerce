# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import request
from openerp.sql_db import TestCursor
from openerp.addons.website_sale.controllers.main import website_sale


class RequireLegalTermsToCheckout(website_sale):
    def checkout_parse(self, address_type, data, remove_prefix=False,
                       *args, **kwargs):
        """Require accepting legal terms to buy."""
        result = (super(RequireLegalTermsToCheckout, self).
                  checkout_parse(address_type, data, remove_prefix,
                                 *args, **kwargs))

        # Avoid PhantomJS errors in test mode
        if (not isinstance(request.env.cr, TestCursor) and
                address_type == "billing"):
            result["accepted_legal_terms"] = (
                bool(request.params.get("accepted_legal_terms")))

        return result

    def checkout_form_save(self, checkout, *args, **kwargs):
        """Do not use accepting legal terms to save."""
        if "accepted_legal_terms" in checkout:
            del checkout["accepted_legal_terms"]

        return super(RequireLegalTermsToCheckout, self).checkout_form_save(
            checkout, *args, **kwargs)

    def checkout_form_validate(self, data, *args, **kwargs):
        """Require accepting legal terms to buy."""
        errors = (super(RequireLegalTermsToCheckout, self)
                  .checkout_form_validate(data, *args, **kwargs))

        # If it is ``None``, then there is no need to check it
        if data.get("accepted_legal_terms") is False:
            errors["accepted_legal_terms"] = "missing"

        return errors
