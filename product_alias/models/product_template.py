# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_alias_ids = fields.One2many(
        comodel_name="product.alias",
        inverse_name="product_tmpl_id",
        string="Product Aliases",
    )
