# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def signup(self, values, token=None):
        if token:
            partner = self.env["res.partner"]._signup_retrieve_partner(
                token, check_validity=True, raise_exception=True
            )
            partner_user = partner.user_ids and partner.user_ids[0] or False
            # Don't update fiscal_position_type if partner related to user
            # exists (i.e. when resetting password)
            if partner_user:
                values.pop("fiscal_position_type", None)
        return super().signup(values, token)

    def _create_user_from_template(self, values):
        user = super()._create_user_from_template(values)
        if user and user.partner_id and values.get("fiscal_position_type"):
            user.partner_id.write(
                {"fiscal_position_type": values.get("fiscal_position_type")}
            )
        return user
