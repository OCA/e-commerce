# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import str2bool


class ResPartner(models.Model):
    _inherit = "res.partner"

    restrict_products = fields.Boolean(
        help="Enable to restrict products based on the assigned pricelist."
    )
    restrict_products_for_all_users = fields.Boolean(
        compute="_compute_restrict_products_for_all_users", store=False
    )

    def _compute_restrict_products_for_all_users(self):
        param_value = str2bool(
            self.env["ir.config_parameter"].sudo().get_param(
                "website_sale_restrict_by_pricelist.restrict_products", default="False"
            )
        )
        for partner in self:
            partner.restrict_products_for_all_users = param_value
