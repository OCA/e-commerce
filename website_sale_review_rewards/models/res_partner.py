# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def compute_reviews_count(self):
        self.ensure_one()
        model_id = self.env.ref("website_sale.model_product_template")
        rating_ids = self.env["rating.rating"].search(
            [
                ("res_model_id", "=", model_id.id),
                ("res_id", "!=", None),
                ("partner_id", "=", self.id),
                ("consumed", "=", True),
            ]
        )
        message_ids = self.env["mail.message"].search(
            [
                ("model", "=", "product.template"),
                ("author_id", "=", self.id),
                ("message_type", "=", "comment"),
                ("is_internal", "=", False),
            ]
        )
        rating_count = len(rating_ids)
        message_count = len(message_ids)
        return max(rating_count, message_count)
