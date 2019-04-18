# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo.tests


class TestUi(odoo.tests.HttpCase):
    def run_tour(self, login=None):
        self.phantom_js(
            "/",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".run('shop_buy_product')",

            "odoo.__DEBUG__.services['web_tour.tour']"
            ".tours.shop_buy_product.ready",

            login=login
        )

    # keep test numbering from module website_sale.
    # Test 01 is not needed in this module
    def test_02_admin_checkout(self):
        self.run_tour("admin")

    def test_03_demo_checkout(self):
        self.run_tour("demo")

    def test_04_public_checkout(self):
        # Disable sign up, in case auth_signup is installed
        self.env["ir.config_parameter"].set_param(
            "auth_signup.invitation_scope", "b2b")
        self.run_tour()
