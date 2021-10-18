from odoo import fields, models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many("website", string="Websites")

    def can_access_from_current_website(self, website_id=False):
        website_id = website_id or request.website.id
        for rec in self.filtered(lambda x: x.website_ids):
            if website_id not in rec.website_ids.ids:
                return False
        return True
