# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests


@odoo.tests.tagged("post_install", "-at_install")
class UICase(odoo.tests.HttpCase):
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

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_product_brand", login="portal")
