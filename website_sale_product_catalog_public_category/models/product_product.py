# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # The search panel only displays many2one or selection fields as a
    # hierarchical category, so this field exposes public_categ_ids as one
    public_categ_id = fields.Many2one(
        comodel_name="product.public.category",
        string="Website Category",
        compute="_compute_public_categ_id",
        search="_search_public_categ_id",
    )

    def _compute_public_categ_id(self):
        for product in self:
            product.public_categ_id = product.public_categ_ids[:1]

    def _search_public_categ_id(self, operator, value):
        return [("public_categ_ids", operator, value)]

    @api.model
    def _search_panel_field_image(self, field_name, **kwargs):
        # public_categ_id is not stored, so it cannot be grouped: take the
        # categories used by the products from public_categ_ids instead
        if field_name == "public_categ_id":
            field_name = "public_categ_ids"
        return super()._search_panel_field_image(field_name, **kwargs)
