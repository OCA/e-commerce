# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_template_link_ids = fields.One2many(
        string="Product Links",
        comodel_name="product.template.link",
        compute="_compute_product_link_ids",
    )

    product_template_link_count = fields.Integer(
        string="Product Links Count", compute="_compute_product_template_link_count"
    )

    def _compute_product_link_ids(self):
        link_model = self.env["product.template.link"]
        domain = [
            "|",
            ("left_product_tmpl_id", "in", self.ids),
            ("right_product_tmpl_id", "in", self.ids),
        ]
        links = link_model.search(domain)
        links_by_product_id = defaultdict(set)
        for link in links:
            links_by_product_id[link.left_product_tmpl_id.id].add(link.id)
            links_by_product_id[link.right_product_tmpl_id.id].add(link.id)
        for record in self:
            record.product_template_link_ids = self.env["product.template.link"].browse(
                list(links_by_product_id[record.id])
            )

    @api.depends("product_template_link_ids")
    def _compute_product_template_link_count(self):
        link_model = self.env["product.template.link"]
        # Set product_template_link_qty to 0 if user has no access on the model
        try:
            link_model.check_access_rights("read")
        except AccessError:
            for rec in self:
                rec.product_template_link_count = 0
            return

        domain = [
            "|",
            ("left_product_tmpl_id", "in", self.ids),
            ("right_product_tmpl_id", "in", self.ids),
        ]

        res_1 = link_model.read_group(
            domain=domain,
            fields=["left_product_tmpl_id"],
            groupby=["left_product_tmpl_id"],
        )
        res_2 = link_model.read_group(
            domain=domain,
            fields=["right_product_tmpl_id"],
            groupby=["right_product_tmpl_id"],
        )

        link_dict = {}
        for dic in res_1:
            link_id = dic["left_product_tmpl_id"][0]
            link_dict.setdefault(link_id, 0)
            link_dict[link_id] += dic["left_product_tmpl_id_count"]
        for dic in res_2:
            link_id = dic["right_product_tmpl_id"][0]
            link_dict.setdefault(link_id, 0)
            link_dict[link_id] += dic["right_product_tmpl_id_count"]

        for rec in self:
            rec.product_template_link_count = link_dict.get(rec.id, 0)

    def show_product_template_links(self):
        self.ensure_one()

        return {
            "name": _("Product links"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "product.template.link",
            "domain": [
                "|",
                ("left_product_tmpl_id", "=", self.id),
                ("right_product_tmpl_id", "=", self.id),
            ],
            "context": {
                "search_default_groupby_type": True,
                "default_left_product_tmpl_id": self.id,
            },
        }
