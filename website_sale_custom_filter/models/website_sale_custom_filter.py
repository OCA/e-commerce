# Copyright 2022 Camptocamp
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class WebsiteSaleCustomFilter(models.Model):
    _name = "website.sale.custom.filter"
    _description = "website.sale.custom.filter"
    _inherit = "mail.thread"

    def _default_website(self):
        return self.env["website"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    def _prepare_filter_default_website_values(self):
        self.ensure_one()
        values = {}
        col_name = self.numerical_filter_field_id.name
        model_name = self.numerical_filter_field_id.model
        if model_name == "product.product":
            # there are fields related to product.template sometimes
            model_name = "product.template"
        query = f"""
            SELECT MIN({col_name}),
            MAX({col_name})
            FROM {self.env[model_name]._table}
        """
        # pylint: disable=E8103
        self.env.cr.execute(query)
        available_min_value, available_max_value = self.env.cr.fetchone()
        values["available_min_value"] = available_min_value
        values["available_max_value"] = available_max_value
        values["min_value"] = available_min_value
        values["max_value"] = available_max_value
        return values

    name = fields.Char(required=True, string="Filter name", translate=True)
    sequence = fields.Integer(default=10)
    website_category_ids = fields.Many2many(
        "product.public.category", required=True, string="Website category"
    )
    filter_collapsed = fields.Boolean()
    filter_type = fields.Selection(
        [("numerical", "Numerical"), ("value", "Value based"), ("color", "Color")],
        default="numerical",
    )
    product_model_id = fields.Many2one(
        "ir.model",
        readonly=True,
        default=lambda self: self.env.ref("product.model_product_product"),
    )
    numerical_filter_field_id = fields.Many2one(
        "ir.model.fields",
        string="Numerical filter",
        domain="[('ttype','in',('float','integer')),('model_id','=','product.product')]",
    )
    custom_filter_value_ids = fields.One2many(
        "website.sale.custom.filter.value",
        "custom_filter_id",
        string="Custom filter values",
        store=True,
    )
    website_ids = fields.Many2many(
        "website",
        relation="filter_website_rel",
        string="website",
        default=_default_website,
        ondelete="cascade",
    )
    min_value = fields.Float()
    max_value = fields.Float()
