# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class WebsiteSaleCustomFilterValue(models.Model):
    _name = "website.sale.custom.filter.value"
    _description = "website.sale.custom.filter.value"
    _order = "sequence"

    @api.depends("value_filter_id.domain")
    def _compute_selected_product_templates(self):
        ProductTemplate = self.env["product.template"]
        for res in self:
            res.selected_product_tmpl_ids = False
            if res.value_filter_id and res.value_filter_id.domain:
                res.selected_product_tmpl_ids = ProductTemplate.search(
                    res.value_filter_id._get_eval_domain()
                )

    name = fields.Char(required=True, string="Value name", translate=True)
    sequence = fields.Integer(required=True, default=10)
    custom_filter_id = fields.Many2one(
        "website.sale.custom.filter",
        ondelete="cascade",
        required=True,
        string="Filter ID",
    )
    value_filter_id = fields.Many2one("ir.filters", string="Value filter ID")
    selected_product_tmpl_ids = fields.Many2many(
        "product.template",
        string="Selected product template",
        readonly=True,
        compute="_compute_selected_product_templates",
        compute_sudo=True,
    )

    html_color = fields.Char(
        string="Color", help="Here you can set a specific HTML color."
    )
