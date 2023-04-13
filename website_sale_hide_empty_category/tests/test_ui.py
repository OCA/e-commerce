# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        category_posted = self.env["product.public.category"].create(
            {"name": "Category Test Posted"}
        )
        self.env["product.public.category"].create({"name": "Category Test Not Posted"})
        self.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "public_categ_ids": [category_posted.id],
            }
        )
        self.env.ref("website_sale.products_categories").active = True

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_hide_empty_category",
            login="admin",
        )
