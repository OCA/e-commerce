# Copyright 2025 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _frontend_pre_dispatch(cls):
        res = super()._frontend_pre_dispatch()
        if request.session.get("tax_toggle_taxed") is None:
            request.session["tax_toggle_taxed"] = (
                request.env.website.tax_display == "tax_included"
            )
        return res
