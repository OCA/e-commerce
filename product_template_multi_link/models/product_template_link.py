# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplateLink(models.Model):
    _name = "product.template.link"
    _order = "left_product_tmpl_id, right_product_tmpl_id"
    _description = "Product link"

    left_product_tmpl_id = fields.Many2one(
        string="Source Product",
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    left_product_img = fields.Image(
        string="Left Product Image", related="left_product_tmpl_id.image_128"
    )
    right_product_tmpl_id = fields.Many2one(
        string="Linked Product",
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
        index=True,
    )
    right_product_img = fields.Image(
        string="Right Product Image", related="right_product_tmpl_id.image_128"
    )
    type_id = fields.Many2one(
        string="Link type",
        comodel_name="product.template.link.type",
        required=True,
        ondelete="restrict",
        index=True,
    )
    link_type_name = fields.Char(related="type_id.name")  # left to right
    link_type_inverse_name = fields.Char(
        related="type_id.inverse_name"
    )  # right to left
    is_link_active = fields.Boolean(compute="_compute_is_link_active")

    def _compute_is_link_active(self):
        # Hook here to define your own logic
        for record in self:
            record.is_link_active = True

    @api.constrains("left_product_tmpl_id", "right_product_tmpl_id", "type_id")
    def _check_products(self):
        """Verify links between products.

        Check whether:
            - the two products are different
            - there is only one link between the same two templates for the same type

        :raise: ValidationError if not ok
        """
        self.flush_recordset()  # flush required since the method uses plain sql
        if any(rec._check_product_not_different() for rec in self):
            raise ValidationError(
                self.env._("You can only create a link between 2 different products")
            )

        products = self.mapped("left_product_tmpl_id") + self.mapped(
            "right_product_tmpl_id"
        )
        query, query_args = self._check_products_query(products)
        self.env.cr.execute(query, query_args)
        res = self.env.cr.fetchall()
        is_duplicate_by_link_id = dict(res)
        if True in is_duplicate_by_link_id.values():
            ids = [k for k, v in is_duplicate_by_link_id.items() if v]
            descrs = "\n ".join(
                [link._duplicate_link_error_msg() for link in self.browse(ids)]
            )
            raise ValidationError(
                self.env._(
                    "Only one link with the same type is allowed between 2 "
                    "products. \n %s"
                )
                % descrs
            )

    def _check_product_not_different(self):
        return self.left_product_tmpl_id == self.right_product_tmpl_id

    def _check_products_query(self, products):
        query = """
            SELECT
                id,
                l2.duplicate or l3.duplicate
            FROM (
                SELECT
                    {main_select_columns}
                FROM
                    %s
                WHERE
                    left_product_tmpl_id in %s
                    AND right_product_tmpl_id in %s
            ) as l1
            LEFT JOIN LATERAL (
                SELECT
                    TRUE as duplicate
                FROM
                    %s
                WHERE
                    {l2_join_where_clause}
            ) l2 ON TRUE
            LEFT JOIN LATERAL (
                SELECT
                    TRUE as duplicate
                FROM
                    %s
                WHERE
                    {l3_join_where_clause}
            ) l3 ON TRUE
        """.format(**self._check_products_query_params())
        query_args = (
            AsIs(self._table),
            tuple(products.ids),
            tuple(products.ids),
            AsIs(self._table),
            AsIs(self._table),
        )
        return query, query_args

    def _check_products_query_params(self):
        return dict(
            main_select_columns="""
                id,
                left_product_tmpl_id,
                right_product_tmpl_id,
                type_id
            """,
            l2_join_where_clause="""
            right_product_tmpl_id = l1.left_product_tmpl_id
            AND left_product_tmpl_id = l1.right_product_tmpl_id
            AND type_id = l1.type_id
        """,
            l3_join_where_clause="""
            left_product_tmpl_id = l1.left_product_tmpl_id
            AND right_product_tmpl_id = l1.right_product_tmpl_id
            AND type_id = l1.type_id
            AND id != l1.id
        """,
        )

    def _duplicate_link_error_msg(self):
        return f"""(
            {self.left_product_tmpl_id.name} <-> {self.link_type_name} /
            {self.link_type_inverse_name} <-> {self.right_product_tmpl_id.name})"""

    @contextmanager
    def _invalidate_links_on_product_template(self):
        yield
        self._invalidate_links()

    def _invalidate_links(self):
        self.env["product.template"].invalidate_model(["product_template_link_ids"])

    @api.model_create_multi
    def create(self, vals_list):
        with self._invalidate_links_on_product_template():
            return super().create(vals_list)

    def write(self, vals):
        with self._invalidate_links_on_product_template():
            return super().write(vals)
