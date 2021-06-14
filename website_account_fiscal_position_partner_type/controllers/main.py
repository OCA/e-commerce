# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request

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
                            afp_obj._fields["fiscal_position_type"].selection
                        ),
                    }
                )
        return res
