# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from odoo.osv import expression


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

    def get_links_by_code(self, code):
        """Get all active active links maching code for current product."""
        self.ensure_one()
        return self.product_template_link_ids.filtered(
            lambda r: r.type_id.code == code and r.is_link_active
        )

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        # NOTE: Odoo limits the search on the name of templates as soon as
        # the 'id' field is present in 'args' domain, and this 'id' criteria is
        # set by the view on purpose to avoid a search on variants.
        # Improve this search by looking also on template's default_code
        # if there is only a domain on 'id'.
        search_default_code = self.env.context.get("name_search_default_code")
        if name and len(args or []) == 1 and args[0][0] == "id" and search_default_code:
            args = expression.AND(
                [
                    args,
                    expression.OR(
                        [
                            [("default_code", operator, name)],
                            [("product_variant_ids.default_code", operator, name)],
                            [(self._rec_name, operator, name)],
                        ]
                    ),
                ]
            )
            # Reset 'name' so base '_name_search' won't add '_rec_name'
            # to 'args' (already added above).
            # See 'odoo.models.BaseModel._name_search'.
            name = ""
        return super()._name_search(
            name=name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
