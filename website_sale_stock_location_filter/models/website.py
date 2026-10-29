# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_website_stock_locations(self):
        """Return the internal locations whose stock is published on the shop.

        Internal locations flagged with ``exclude_from_website_stock`` (e.g.
        technician locations) are left out. When the website has a warehouse,
        only that warehouse's locations are considered; otherwise all the
        internal locations of the active companies are used (mirroring the
        default behaviour of ``free_qty`` without a warehouse context).

        Runs sudo: the shop exposes stock to public/portal visitors, who have
        no read access to ``stock.location``. Standard ``free_qty`` never reads
        locations directly (it goes through warehouses and sudoes the quants),
        so resolving the location set ourselves needs the same elevation.
        """
        self.ensure_one()
        domain = [
            ("usage", "=", "internal"),
            ("exclude_from_website_stock", "=", False),
        ]
        if self.warehouse_id:
            domain.append(("id", "child_of", self.warehouse_id.view_location_id.id))
        else:
            domain.append(("company_id", "in", self.env.companies.ids))
        return self.env["stock.location"].sudo().search(domain)

    def _get_product_available_qty(self, product, **kwargs):
        locations = self._get_website_stock_locations()
        if not locations:
            return 0.0
        # ``strict=True`` makes ``free_qty`` count exactly these locations,
        # without re-expanding to their children, so excluded sub-locations
        # stay excluded. See stock.product._get_domain_locations_new.
        return product.with_context(location=locations.ids, strict=True).free_qty
