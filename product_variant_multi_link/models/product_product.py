# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_variant_link_ids = fields.One2many(
        string="Product Variant Links",
        comodel_name="product.template.link",
        compute="_compute_product_link_ids",
    )

    product_product_link_count = fields.Integer(
        string="Variants Links Count", compute="_compute_product_product_link_count"
    )

    @api.depends("product_variant_link_ids")
    def _compute_product_product_link_count(self):
        link_model = self.env["product.template.link"]
        # Set product_template_link_qty to 0 if user has no access on the model
        try:
            link_model.check_access_rights("read")
        except AccessError:
            self.update({"product_product_link_count": 0})
            return

        domain = [
            "|",
            ("left_product_id", "in", self.ids),
            ("right_product_id", "in", self.ids),
        ]

        res_1 = link_model.read_group(
            domain=domain, fields=["left_product_id"], groupby=["left_product_id"],
        )
        res_2 = link_model.read_group(
            domain=domain, fields=["right_product_id"], groupby=["right_product_id"],
        )

        link_dict = {}
        for dic in res_1:
            link_id = dic["left_product_id"][0]
            link_dict.setdefault(link_id, 0)
            link_dict[link_id] += dic["left_product_id_count"]
        for dic in res_2:
            link_id = dic["right_product_id"][0]
            link_dict.setdefault(link_id, 0)
            link_dict[link_id] += dic["right_product_id_count"]

        for rec in self:
            rec.product_product_link_count = link_dict.get(rec.id, 0)

    def _compute_product_link_ids(self):
        for record in self:
            record.product_variant_link_ids = record._get_variant_links()

    def _get_variant_links(self):
        return self.product_template_link_ids.filtered_domain(
            ["|", ("left_product_id", "=", self.id), ("right_product_id", "=", self.id)]
        )

    def show_product_product_links(self):
        self.ensure_one()

        return {
            "name": _("Product links"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "product.template.link",
            "domain": [
                "|",
                ("left_product_id", "=", self.id),
                ("right_product_id", "=", self.id),
            ],
            "context": {
                "search_default_groupby_type": True,
                "default_left_product_id": self.id,
            },
        }
