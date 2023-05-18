# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductWishlist(models.Model):
    _inherit = "product.wishlist"

    @api.model
    def _process_wishlist_archive(self):
        wishlist_records = self.search([("active", "=", True)])
        wishlist_records_to_archive = wishlist_records.filtered(
            lambda x: not x.product_id.active
        )
        wishlist_records_to_archive.write({"active": False})
