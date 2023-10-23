# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
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
