# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restrict_products_for_all_users = fields.Boolean(
        help="Enable to restrict products base on the assigned pricelist of all users.",
        config_parameter="website_sale_restrict_by_pricelist.restrict_products",
    )
