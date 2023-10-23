# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("-at_install", "post_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env["product.template"].create(
            {
                "name": "Test Product",
                "website_published": True,
                "website_sequence": 5000,
                "type": "consu",
            }
        )
        cls.env.ref("website_sale_wishlist_keep.default_active_b2b_wish").active = True

    def test_ui_wishlist(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_wishlist_keep", login="admin")
