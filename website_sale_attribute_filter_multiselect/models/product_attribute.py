# Copyright 2021 Studio73 - Ioan Galan
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    display_type = fields.Selection(
        selection_add=[("multiselect", "Multiple Select")],
        ondelete={"multiselect": lambda recs: recs.write({"display_type": "radio"})},
    )
