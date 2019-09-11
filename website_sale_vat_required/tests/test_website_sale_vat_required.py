# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestUi(HttpCase):
    def test_website_sale_vat_required(self):
        self.env.user.partner_id.vat = False
        self.browser_js(
            url_path="/",
            code="odoo.__DEBUG__.services['web_tour.tour']"
                 ".run('shop_buy_product')",
            ready="odoo.__DEBUG__.services['web_tour.tour']"
                  ".tours.shop_buy_product.ready",
            login="admin",
        )
