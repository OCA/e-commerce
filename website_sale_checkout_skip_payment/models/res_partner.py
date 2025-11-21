# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    skip_website_checkout_payment = fields.Boolean(default=False)

    @api.model
    def _commercial_fields(self):
        """Add this field to commercial fields, as it should be propagated
        to children.
        """
        return super()._commercial_fields() + ["skip_website_checkout_payment"]
