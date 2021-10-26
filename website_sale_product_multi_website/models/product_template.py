from odoo import api, fields, models
from odoo.http import request
from odoo.osv import expression
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
        if not isinstance(value, bool) or operator not in ('=', '!='):
            _logger.warning('unsupported search on website_published: %s, %s', operator, value)
            return [()]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            value = not value

        current_website_id = self._context.get('website_id')
        is_published = [('is_published', '=', value)]
        if current_website_id:
            on_current_website = ['|'] + [('website_ids', 'ilike', item) for item in (False, current_website_id)]
            return (['!'] if value is False else []) + expression.AND([is_published, on_current_website])
        else:  # should be in the backend, return things that are published anywhere
            return is_published
