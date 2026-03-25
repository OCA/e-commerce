# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class Website(models.Model):
    _inherit = "website"

    @api.model
    def website_domain(self, website_id=False):
        # Keep the standard behavior by default, but allow specific flows to switch
        # the website restriction from website_id to website_ids through context.
        if self._context.get("multi_website_domain"):
            return [
                "|",
                ("website_ids", "=", False),
                ("website_ids", "=", website_id or self.id),
            ]
        return super().website_domain(website_id=website_id)

    def sale_product_domain(self):
        # Reuse the standard published search while enabling the multi-website
        # variant of website_domain() used in website sale flows.
        return super(
            Website, self.with_context(multi_website_domain=True)
        ).sale_product_domain()
