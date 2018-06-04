# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import request
from openerp.sql_db import TestCursor
from openerp import SUPERUSER_ID
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
        """Do not use accepting legal terms to save and get metadata"""
        res = super(RequireLegalTermsToCheckout, self).checkout_form_save(
            checkout, *args, **kwargs)
        if "accepted_legal_terms" in checkout:
            del checkout["accepted_legal_terms"]
            user_obj = request.env['res.users']
            order = request.website.sale_get_order(
                force_create=1, context=request.context)
            partner_id = request.env['res.partner']
            if request.uid != request.website.user_id.id:
                partner_id = user_obj.browse(request.uid).partner_id
            elif order.partner_id:
                user_ids = user_obj.with_context(
                    dict(request.context, active_test=False)).search(
                    [("partner_id", "=", order.partner_id.id)])
                if not user_ids or request.website.user_id.id not in user_ids:
                    partner_id = order.partner_id
            if partner_id:
                environ = request.httprequest.headers.environ
                metadata = "Website legal terms acceptance metadata:<br/>"
                metadata += "<br/>".join(
                    "%s: %s" % (val, environ.get(val)) for val in (
                            "REMOTE_ADDR",
                            "HTTP_USER_AGENT",
                            "HTTP_ACCEPT_LANGUAGE",
                        )
                    )
                website_user = (request.website.salesperson_id.id or
                                SUPERUSER_ID)
                partner_id.sudo(website_user).message_post(body=metadata)
        return res

    def checkout_form_validate(self, data, *args, **kwargs):
        """Require accepting legal terms to buy."""
        errors = (super(RequireLegalTermsToCheckout, self)
                  .checkout_form_validate(data, *args, **kwargs))

        # If it is ``None``, then there is no need to check it
        if data.get("accepted_legal_terms") is False:
            errors["accepted_legal_terms"] = "missing"

        return errors
