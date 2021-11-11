# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests


@odoo.tests.tagged("post_install", "-at_install")
class UICase(odoo.tests.HttpCase):
    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_product_brand", login="portal")
