# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestUICustomerReviews(common.HttpCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.product = cls.env.ref("website_sale_customer_reviews.product_test_review")
        return res

    def test_reviews(self):
        statisctics = self.product.rating_get_stats()
        percent = statisctics["percent"]
        self.assertEqual(round(percent[1], 1), 16.7)
        self.assertEqual(round(percent[2], 1), 33.3)
        self.assertEqual(round(percent[3], 1), 50.0)

    def test_ui(self):
        self.start_tour(
            "/shop/category/desks-1",
            "website_sale_customer_reviews_tour",
            login="admin",
            step_delay=1000,
            debug=False,
        )
