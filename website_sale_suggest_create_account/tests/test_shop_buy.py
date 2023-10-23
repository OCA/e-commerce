# Copyright (C) 2020 Alexandre Díaz - Tecnativa S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import odoo.tests


@odoo.tests.tagged("post_install", "-at_install")
class TestUi(odoo.tests.HttpCase):
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

    def test_01_shop_buy(self):
        # Ensure that 'vat' is not empty for compatibility with
        # website_sale_vat_required module
        portal_user = self.env.ref("base.demo_user0")
        if not portal_user.partner_id.vat:
            portal_user.partner_id.vat = "BE1234567"
        current_website = self.env["website"].get_current_website()
        current_website.auth_signup_uninvited = "b2b"
        self.env.ref("website_sale_suggest_create_account.cart").active = True
        self.env.ref(
            "website_sale_suggest_create_account.short_cart_summary"
        ).active = True
        self.start_tour("/shop", "shop_buy_checkout_suggest_account_website")
