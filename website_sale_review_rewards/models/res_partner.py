# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def count_customer_reviews(self, start_date=None, end_date=None):
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
        count = 0
        if start_date and end_date:
            for rating_id in rating_ids:
                create_date = rating_id.create_date.date()
                if create_date >= start_date and create_date <= end_date:
                    count += 1
        else:
            rating_count = len(rating_ids)
            message_count = len(message_ids)
            count = max(rating_count, message_count)
        return count

    def compute_reviews_count(self, goal_id=None):
        self.ensure_one()
        count = 0
        if goal_id:
            challenge_id = goal_id.challenge_id
            start_date = challenge_id.start_date
            end_date = challenge_id.end_date
            count = self.count_customer_reviews(start_date, end_date)
        return count
