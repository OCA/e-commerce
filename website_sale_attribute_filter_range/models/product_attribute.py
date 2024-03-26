# Copyright 2021 Studio73 - Miguel Gandia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    display_type = fields.Selection(
        selection_add=[("range", "Range")],
        ondelete={"range": lambda recs: recs.write({"display_type": "radio"})},
    )
