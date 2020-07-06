# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestUi(HttpCase):
    def setUp(self):
        super().setUp()
        self.env["product.template"].create(
            {
                "name": "Test Product",
                "website_published": True,
                "website_sequence": 5000,
                "type": "consu",
            }
        )
        self.env.ref('website_sale_wishlist_keep.default_active_b2b_wish').active = True

    def test_ui_wishlist(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_wishlist_keep",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
