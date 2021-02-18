# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ProductTemplateLink(models.Model):
    _inherit = "product.template.link"

    left_product_id = fields.Many2one(
        string="Source Variant", comodel_name="product.product", ondelete="cascade",
    )
    right_product_id = fields.Many2one(
        string="Linked Variant", comodel_name="product.product", ondelete="cascade",
    )

    def _product_variant_check_enabled(self):
        # You might want to turn off the check on variants, here's your chance
        return not self.env.context.get("_product_variant_link_bypass_check")

    @api.constrains(
        "left_product_tmpl_id",
        "right_product_tmpl_id",
        "type_id",
        "left_product_id",
        "right_product_id",
    )
    def _check_products(self):
        if self._product_variant_check_enabled():
            for rec in self:
                # make new fields required here
                # to avoid issues w/ existing table and existing records
                if not rec.left_product_id or not rec.right_product_id:
                    raise exceptions.ValidationError(
                        _("Source and target variants are required!")
                    )
        super()._check_products()

    @api.onchange("left_product_tmpl_id")
    def onchange_left_product_tmpl(self):
        self.ensure_one()
        domain = []
        if self.left_product_tmpl_id:
            # Remove left_product_id if its template doesn't match anymore
            if self.left_product_id.product_tmpl_id != self.left_product_tmpl_id:
                self.left_product_id = False
            domain = [("product_tmpl_id", "=", self.left_product_tmpl_id.id)]
        else:
            self.left_product_id = False
        return {"domain": {"left_product_id": domain}}

    @api.onchange("left_product_id")
    def onchange_left_product(self):
        self.ensure_one()
        if self.left_product_id:
            self.left_product_tmpl_id = self.left_product_id.product_tmpl_id

    @api.onchange("right_product_tmpl_id")
    def onchange_right_product_tmpl(self):
        self.ensure_one()
        domain = []
        if self.right_product_tmpl_id:
            # Remove right_product_id if its template doesn't match anymore
            if self.right_product_id.product_tmpl_id != self.right_product_tmpl_id:
                self.right_product_id = False
            domain = [("product_tmpl_id", "=", self.right_product_tmpl_id.id)]
        else:
            self.right_product_id = False
        return {"domain": {"right_product_id": domain}}

    @api.onchange("right_product_id")
    def onchange_right_product(self):
        self.ensure_one()
        if self.right_product_id:
            self.right_product_tmpl_id = self.right_product_id.product_tmpl_id

    def _check_product_not_different(self):
        res = super()._check_product_not_different()
        if self._product_variant_check_enabled():
            return res and self.left_product_id == self.right_product_id
        return res

    def _check_products_query_params(self):
        params = super()._check_products_query_params()
        if self._product_variant_check_enabled():
            params["main_select_columns"] += ", right_product_id, left_product_id"
            params[
                "l2_join_where_clause"
            ] += """
                AND right_product_id = l1.left_product_id
                AND left_product_id = l1.right_product_id
            """
            params[
                "l3_join_where_clause"
            ] += """
                AND left_product_id = l1.left_product_id
                AND right_product_id = l1.right_product_id
            """
        return params

    def _invalidate_links(self):
        super()._invalidate_links()
        self.env["product.product"].invalidate_cache(["product_variant_link_ids"])
