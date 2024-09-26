# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    expected_publish_date = fields.Datetime()
    expected_unpublish_date = fields.Datetime()

    def _get_publish_date_domain(self):
        """Generate domain for publish and unpublish date filtering."""
        now = fields.Datetime.now()
        return [
            "|",
            "&",
            ("expected_publish_date", "<=", now),
            "|",
            ("expected_unpublish_date", ">=", now),
            ("expected_unpublish_date", "=", False),
            "&",
            ("expected_publish_date", "=", False),
            "|",
            ("expected_unpublish_date", ">=", now),
            ("expected_unpublish_date", "=", False),
        ]

    @api.model
    def _search_build_domain(self, domain_list, search, fields, extra=None):
        base_domain = super()._search_build_domain(domain_list, search, fields, extra)
        publish_date_domain = self._get_publish_date_domain()
        combined_domain = expression.AND([base_domain, publish_date_domain])
        return combined_domain
