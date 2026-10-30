# Copyright 2026 Domatix
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class WebsiteSaleStickyAddToCartCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Minimal 1x1 red PNG.
        image = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGM4oaEBAALUA"
            "RkFUI+kAAAAAElFTkSuQmCC"
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Sticky Bar Demo Product",
                "type": "consu",
                "sale_ok": True,
                "website_published": True,
                "list_price": 125.0,
                "image_1920": image,
            }
        )

    def test_sticky_bar_rendered(self):
        """The sticky bar is rendered on a published product page."""
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("o_sticky_add_to_cart_bar", response.text)

    def test_tour_website(self):
        """Frontend tour: the bar appears on scroll and keeps the price."""
        self.start_tour(
            "/shop", "website_sale_product_sticky_add_to_cart", login="admin"
        )
