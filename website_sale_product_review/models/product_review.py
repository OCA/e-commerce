# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductReview(models.Model):
    _name = "product.review"
    _description = "Product Review"

    product_id = fields.Many2one(
        "product.template", string="Product", required=True, ondelete="cascade"
    )
    partner_id = fields.Many2one("res.partner", related="create_uid.partner_id")
    rating = fields.Selection(
        selection=[(str(i), f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
        required=True,
    )
    comment = fields.Text()
