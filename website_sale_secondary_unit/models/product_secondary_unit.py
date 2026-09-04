# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductSecondaryUnit(models.Model):
    _inherit = ["product.secondary.unit", "website.published.mixin"]
    _name = "product.secondary.unit"

    is_published = fields.Boolean(default=True)

    def _filter_website_published(self):
        """Units the customer is allowed to see and pick in the shop."""
        return self.filtered(lambda su: su.active and su.is_published)

    def _get_website_display_name(self):
        """Label shown to the customer in the shop, e.g. ``Box 5 Units``.

        The product unit of measure is omitted when it would only repeat the
        secondary unit name (e.g. a secondary unit named ``Units``).
        """
        self.ensure_one()
        unit = self.sudo()
        factor = int(unit.factor) if int(unit.factor) == unit.factor else unit.factor
        uom_name = unit.product_tmpl_id.uom_id.name
        display_name = f"{unit.name} {factor}"
        if uom_name != unit.name:
            display_name = f"{display_name} {uom_name}"
        return display_name
