# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    website_url = fields.Char(
        string="Website URL",
        compute="_compute_website_url",
    )

    @api.depends("seo_name")
    @api.depends_context("lang")
    def _compute_website_url(self):
        for category in self:
            if category.id:
                category.website_url = (
                    f"/shop/category/{self.env['ir.http']._slug(category)}"
                )
            else:
                category.website_url = "#"

    def open_website_url(self):
        self.ensure_one()
        return self.env["website"].get_client_action(self.website_url)
