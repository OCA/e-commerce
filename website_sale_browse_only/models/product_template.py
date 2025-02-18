from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _website_show_quick_add(self):
        website = self.env["website"].get_current_website()
        return not website.browse_only and super()._website_show_quick_add()
