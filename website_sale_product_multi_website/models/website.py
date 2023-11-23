from odoo import api, models


class Website(models.Model):

    _inherit = "website"

    @api.model
    def website_domain(self, website_id=False):
        if self._context.get("multi_website_domain"):
            return [
                "|",
                ("website_ids", "=", False),
                ("website_ids", "=", website_id or self.id),
            ]
        return super().website_domain(website_id=website_id)

    def sale_product_domain(self):
        """We add a context in order to change the way that website_domain behavies"""
        return super(
            Website, self.with_context(multi_website_domain=True)
        ).sale_product_domain()
