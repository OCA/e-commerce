# -*- coding: utf-8 -*-
# © 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo.tests


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestUi(odoo.tests.HttpCase):
    def test_01_public_checkout(self):
        self.phantom_js("/",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".run('shop_buy_product_osc_public')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours"
                        ".shop_buy_product_osc_public.ready")

    def test_02_demo_checkout(self):
        self.phantom_js("/",
                        "odoo.__DEBUG__.services['web_tour.tour']"
                        ".run('shop_buy_product_osc_demo')",
                        "odoo.__DEBUG__.services['web_tour.tour'].tours"
                        ".shop_buy_product_osc_demo.ready",
                        login="demo")
