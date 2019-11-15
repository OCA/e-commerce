# Copyright 2017-Today GRAP (http://www.grap.coop).
# @author Sylvain LE GAL <https://twitter.com/legalsylvain>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_template_link_ids = fields.One2many(
        string="Product Links",
        comodel_name="product.template.link",
        inverse_name="product_template_id",
    )

    product_template_link_qty = fields.Integer(
        string="Product Links Quantity",
        compute="_compute_product_template_link_qty",
        store=True,
    )

    @api.depends("product_template_link_ids")
    def _compute_product_template_link_qty(self):
        for template in self:
            template.product_template_link_qty = len(template.product_template_link_ids)
