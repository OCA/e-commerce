# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values, errors, error_msg = super(WebsiteSale, self).values_postprocess(
            order=order, mode=mode, values=values, errors=errors, error_msg=error_msg
        )
        if mode[1] in ("billing") and values.get("fiscal_position_type", False):
            new_values.update(
                {"fiscal_position_type": values.get("fiscal_position_type")}
            )
        return new_values, errors, error_msg

    def checkout_form_validate(self, mode, all_form_values, data):
        old_context = request.context
        request.context = dict(
            request.context,
            fiscal_position_type=all_form_values.get("fiscal_position_type"),
        )
        error, error_message = super().checkout_form_validate(
            mode, all_form_values, data
        )
        request.context = old_context
        if data.get("fiscal_position_type"):
            partner_su = (
                request.env["res.partner"]
                .sudo()
                .browse(int(data["partner_id"]))
                .exists()
            )
            fiscal_position_type_change = (
                partner_su
                and "fiscal_position_type" in data
                and data["fiscal_position_type"] != partner_su.fiscal_position_type
            )
            if fiscal_position_type_change and not partner_su.can_edit_vat():
                error["fiscal_position_type"] = "error"
                error_message.append(
                    _(
                        "Changing partner type is not allowed once invoices have "
                        "been issued for your account. Please contact us directly"
                        " for this operation."
                    )
                )
        return error, error_message

    @http.route()
    def address(self, **kw):
        res = super(WebsiteSale, self).address(**kw)
        if res.qcontext:
            mode = res.qcontext.get("mode", False)
            if mode and mode[1] == "billing":
                # Get default position
                def_fiscpostype = (
                    request.website.company_id.default_fiscal_position_type or "b2c"
                )
                # Get position if exist order
                order = request.website.sale_get_order()
                if order.partner_id:
                    def_fiscpostype = order.partner_id.fiscal_position_type
                # if posted, get the last value
                if kw.get("submitted", False):
                    if res.qcontext.get("error", False):
                        def_fiscpostype = kw.get(
                            "fiscal_position_type", def_fiscpostype
                        )
                # get all options
                afp_obj = request.env["account.fiscal.position"].sudo()
                res.qcontext.update(
                    {
                        "def_fiscpostype": def_fiscpostype,
                        "fiscpostypevalues": dict(
                            afp_obj._fields[
                                "fiscal_position_type"
                            ]._description_selection(request.env)
                        ),
                    }
                )
        return res


class AuthSignupHome(AuthSignupHome):
    def get_auth_signup_qcontext(self):
        qcontext = super().get_auth_signup_qcontext()
        qcontext.update(
            {k: v for (k, v) in request.params.items() if k in {"fiscal_position_type"}}
        )
        afp_obj = request.env["account.fiscal.position"].sudo()
        qcontext["fiscpostypevalues"] = dict(
            afp_obj._fields["fiscal_position_type"]._description_selection(request.env)
        )
        if not qcontext.get("fiscal_position_type_selected"):
            def_fiscpostype = (
                request.website.company_id.default_fiscal_position_type or "b2c"
            )
            qcontext["fiscal_position_type_selected"] = def_fiscpostype
        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = super()._prepare_signup_values(qcontext)
        if "fiscal_position_type" in qcontext:
            values["fiscal_position_type"] = qcontext["fiscal_position_type"]
        return values
