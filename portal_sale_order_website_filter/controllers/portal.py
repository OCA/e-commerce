# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request
from odoo.osv import expression

from odoo.addons.sale.controllers import portal


class CustomerPortal(portal.CustomerPortal):
    def _get_website_domain(self):
        return [
            "|",
            ("website_id", "=", request.website.id),
            ("website_id", "=", False),
        ]

    def _prepare_quotations_domain(self, partner):
        domain = super()._prepare_quotations_domain(partner)
        return expression.AND([domain, self._get_website_domain()])

    def _prepare_orders_domain(self, partner):
        domain = super()._prepare_orders_domain(partner)
        return expression.AND([domain, self._get_website_domain()])
