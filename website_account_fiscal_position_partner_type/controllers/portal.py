# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    CustomerPortal.OPTIONAL_BILLING_FIELDS += ["fiscal_position_type"]

    def details_form_validate(self, data):
        error, error_message = super().details_form_validate(data)
        partner = request.env.user.partner_id
        if (
            not partner.can_edit_vat()
            and "fiscal_position_type" in data
            and data.get("fiscal_position_type") != partner.fiscal_position_type
        ):
            error["fiscal_position_type"] = "error"
            error_message.append(
                _(
                    "Changing Partner Type is not allowed once document(s) have "
                    "been issued for your account. Please contact us directly for"
                    " this operation."
                )
            )
        return error, error_message

    def _prepare_portal_layout_values(self):
        vals = super()._prepare_portal_layout_values()
        afp_obj = request.env["account.fiscal.position"].sudo()
        partner = request.env.user.partner_id
        vals.update(
            {
                "fiscpostypevalues": dict(
                    afp_obj._fields["fiscal_position_type"]._description_selection(
                        request.env
                    )
                ),
                "fiscal_position_type_selected": partner.fiscal_position_type,
            }
        )
        return vals
