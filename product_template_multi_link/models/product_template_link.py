# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
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
    )

    right_product_tmpl_id = fields.Many2one(
        string="Linked Product",
        comodel_name="product.template",
        required=True,
        ondelete="cascade",
    )

    type_id = fields.Many2one(
        string="Link type",
        comodel_name="product.template.link.type",
        required=True,
        ondelete="restrict",
    )

    link_type_name = fields.Char(related="type_id.name")  # left to right
    link_type_inverse_name = fields.Char(
        related="type_id.inverse_name"
    )  # right to left

    @api.constrains("left_product_tmpl_id", "right_product_tmpl_id", "type_id")
    def _check_products(self):
        """
        This method checks whether:
            - the two products are different
            - there is only one link between the same two templates for the same type
        :raise: ValidationError if not ok
        """
        self.flush()  # flush required since the method uses plain sql
        if any(rec.left_product_tmpl_id == rec.right_product_tmpl_id for rec in self):
            raise ValidationError(
                _("You can only create a link between 2 different products")
            )

        products = self.mapped("left_product_tmpl_id") + self.mapped(
            "right_product_tmpl_id"
        )
        self.env.cr.execute(
            """
            SELECT
                id,
                l2.duplicate or l3.duplicate
            FROM (
                SELECT
                    id,
                    left_product_tmpl_id,
                    right_product_tmpl_id,
                    type_id
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
                    right_product_tmpl_id = l1.left_product_tmpl_id
                    AND left_product_tmpl_id = l1.right_product_tmpl_id
                    AND type_id = l1.type_id
            ) l2 ON TRUE
            LEFT JOIN LATERAL (
                SELECT
                    TRUE as duplicate
                FROM
                    %s
                WHERE
                    left_product_tmpl_id = l1.left_product_tmpl_id
                    AND right_product_tmpl_id = l1.right_product_tmpl_id
                    AND type_id = l1.type_id
                    AND id != l1.id
            ) l3 ON TRUE
        """,
            (
                AsIs(self._table),
                tuple(products.ids),
                tuple(products.ids),
                AsIs(self._table),
                AsIs(self._table),
            ),
        )
        res = self.env.cr.fetchall()
        is_duplicate_by_link_id = dict(res)
        if True in is_duplicate_by_link_id.values():
            ids = [k for k, v in is_duplicate_by_link_id.items() if v]
            links = self.browse(ids)
            descrs = []
            for l in links:
                descrs.append(
                    u"{} <-> {} / {} <-> {}".format(
                        l.left_product_tmpl_id.name,
                        l.link_type_name,
                        l.link_type_inverse_name,
                        l.right_product_tmpl_id.name,
                    )
                )
            links = "\n ".join(descrs)
            raise ValidationError(
                _(
                    "Only one link with the same type is allowed between 2 "
                    "products. \n %s"
                )
                % links
            )

    @contextmanager
    def _invalidate_links_on_product_template(self):
        yield
        self.env["product.template"].invalidate_cache(["product_template_link_ids"])

    @api.model
    def create(self, vals_list):
        with self._invalidate_links_on_product_template():
            return super().create(vals_list)

    def write(self, vals):
        with self._invalidate_links_on_product_template():
            return super().write(vals)
