# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class IrFilters(models.Model):
    _inherit = "ir.filters"

    website_availability = fields.Selection(
        selection=[
            ("no_restriction", "Don't apply restriction"),
            ("no_show", "Avoid to show non available products"),
            ("no_purchase", "Avoid selling not available products"),
        ],
        string="Availability on Website",
        default="no_restriction",
        required=True,
        help="""
        Each point is used to:\n
        \t- Don't apply restriction: Show all products available for sale on website.\n
        \t- Avoid to show non available products: Show only products available for sale
        on website.\n
        \t- Avoid selling not available products: Show all products, but avoid
        purchase on website.\n
        """,
    )
    message_unavailable = fields.Char(
        string="Message when unavailable",
        help="""Message showed when some product is not available and the option
        'Avoid selling not available products' is selected.
        """,
    )
    website_ids = fields.Many2many(
        comodel_name="website", ondelete="cascade", string="Websites"
    )
    apply_on_public_user = fields.Boolean()
    assortment_information = fields.Html()
    all_product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="assortment_all_products",
        compute="_compute_all_product_ids",
    )

    @api.depends("domain", "blacklist_product_ids", "whitelist_product_ids")
    def _compute_all_product_ids(self):
        for record in self:
            record.all_product_ids = record.env["product.product"]
            if record.is_assortment:
                record.all_product_ids = record.env["product.product"].search(
                    record._get_eval_domain()
                )

    @api.depends("apply_on_public_user")
    def _compute_all_partner_ids(self):
        super()._compute_all_partner_ids()
        for ir_filter in self:
            if ir_filter.apply_on_public_user:
                ir_filter.all_partner_ids += self.env.ref("base.public_user").partner_id
