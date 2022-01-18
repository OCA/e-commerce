# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import HttpCase


class UICase(HttpCase):
    def setUp(self):
        super().setUp()
        self.website = self.env["website"].get_current_website()
        self.env["product.template"].create(
            {"name": "Test Product 1", "is_published": True, "website_sequence": 1}
        )

    def test_01_add_to_cart_no_redirect(self):
        self.website.cart_add_on_page = True
        self.start_tour("/shop", "add_to_cart_no_redirect", login="admin")
        pass

    def test_02_add_to_cart_redirect(self):
        self.website.cart_add_on_page = False
        self.start_tour("/shop", "add_to_cart_redirect", login="admin")
        pass
