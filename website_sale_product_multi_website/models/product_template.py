from odoo import api, fields, models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    website_ids = fields.Many2many("website", string="Websites")

    def can_access_from_current_website(self, website_id=False):
        """ We overwrite this method completely in order to use the website_ids logic instead of website_id """
        website_id = website_id or request.website.id
        for rec in self.filtered(lambda x: x.website_ids):
            if website_id not in rec.website_ids.ids:
                return False
        return True

    @api.depends('is_published', 'website_ids')
    @api.depends_context('website_id')
    def _compute_website_published(self):
        """ We overwrite this method completely in order to use the website_ids logic instead of website_id """
        current_website_id = self._context.get('website_id')
        for record in self:
            if current_website_id:
                record.website_published = record.is_published and (
                    not record.website_ids or current_website_id in record.website_ids.ids)
            else:
                record.website_published = record.is_published

    def _search_website_published(self, operator, value):
        """ We overwrite this method completely in order to use the website_ids logic instead of website_id """
        return super(ProductTemplate, self.with_context(multi_website_domain=True))._search_website_published(operator, value)
