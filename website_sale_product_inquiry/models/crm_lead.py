# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    inquired_product_id = fields.Many2one(
        "product.product",
        string="Product",
        ondelete="set null",
    )
    inquiry_type = fields.Selection(
        [
            ("more_info", "More Information"),
            ("quote", "Quote"),
        ],
    )
