# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many(
        "website",
        "product_template_website_rel",
        "product_template_id",
        "website_id",
        string="Websites",
        help="Restrict the product to the selected websites. Leave empty to "
        "make it available on all websites.",
    )
    website_id = fields.Many2one(
        "website",
        compute="_compute_website_id",
        inverse="_inverse_website_id",
        store=True,
    )

    @api.depends("website_ids")
    def _compute_website_id(self):
        for record in self:
            record.website_id = record.website_ids[:1]

    def _inverse_website_id(self):
        for record in self:
            if record.website_id and record.website_id not in record.website_ids:
                record.website_ids = [(4, record.website_id.id)]

    def can_access_from_current_website(self, website_id=False):
        # We overwrite this method completely in order to
        # use the website_ids logic instead of website_id
        website_id = website_id or request.env["website"].get_current_website().id
        for record in self:
            website_ids = record.sudo().website_ids.ids
            if website_ids and website_id not in website_ids:
                return False
        return True

    @api.depends("is_published", "website_ids")
    @api.depends_context("website_id")
    def _compute_website_published(self):
        # We overwrite this method completely in order to
        # use the website_ids logic instead of website_id
        current_website_id = self.env.context.get("website_id")
        for record in self:
            website_ids = record.sudo().website_ids
            record.website_published = record.is_published and (
                not current_website_id
                or not website_ids
                or current_website_id in website_ids.ids
            )

    def _search_website_published(self, operator, value):
        # Search with the multi_website_domain context.
        return super(
            ProductTemplate, self.with_context(multi_website_domain=True)
        )._search_website_published(operator, value)
