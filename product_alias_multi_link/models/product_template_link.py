# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplateLink(models.Model):
    _inherit = "product.template.link"

    left_product_alias_id = fields.Many2one(
        string="Source Alias",
        comodel_name="product.alias",
        ondelete="cascade",
    )
    right_product_alias_id = fields.Many2one(
        string="Linked Alias",
        comodel_name="product.alias",
        ondelete="cascade",
    )

    def _product_variant_check_enabled(self):
        # Do not force alias or variants, do with what you have
        return False

    @api.constrains(
        "left_product_tmpl_id",
        "right_product_tmpl_id",
        "type_id",
        "left_product_id",
        "right_product_id",
        "left_product_alias_id",
        "right_product_alias_id",
    )
    def _check_products(self):
        return super()._check_products()

    def _check_product_not_different(self):
        res = super()._check_product_not_different()
        # Link is identical if everything is the same
        return (
            res
            and self.left_product_id == self.right_product_id
            and self.left_product_alias_id == self.right_product_alias_id
        )

    def _check_products_query_params(self):
        params = super()._check_products_query_params()
        # Link is identical if everything is the same on both sides
        params["main_select_columns"] += (
            ", right_product_id, left_product_id"
            ", right_product_alias_id, left_product_alias_id"
        )
        # Use "is not distinct from" to handle NULL values
        params["l2_join_where_clause"] += """
            AND right_product_id is not distinct from l1.left_product_id
            AND left_product_id is not distinct from l1.right_product_id
            AND right_product_alias_id is not distinct from l1.left_product_alias_id
            AND left_product_alias_id is not distinct from l1.right_product_alias_id
        """
        params["l3_join_where_clause"] += """
            AND left_product_id is not distinct from l1.left_product_id
            AND right_product_id is not distinct from l1.right_product_id
            AND left_product_alias_id is not distinct from l1.left_product_alias_id
            AND right_product_alias_id is not distinct from l1.right_product_alias_id
        """
        return params

    def _invalidate_links(self):
        super()._invalidate_links()
        self.env["product.alias"].invalidate_cache(["product_alias_link_ids"])
