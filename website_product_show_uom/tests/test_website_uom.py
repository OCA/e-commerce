# -*- coding: utf-8 -*-
# © 2016 Oscar Alcalá <oscar@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestUi(openerp.tests.HttpCase):
    def test_01_admin_uom(self):
        self.phantom_js(
            "/", "openerp.Tour.run('website_test_uom', 'test')",
            "openerp.Tour.tours.website_test_uom", login="admin")

    def test_02_demo_uom(self):
        self.phantom_js(
            "/", "openerp.Tour.run('website_test_uom', 'test')",
            "openerp.Tour.tours.website_test_uom", login="demo")

    def test_03_public_uom(self):
        self.phantom_js(
            "/", "openerp.Tour.run('website_test_uom', 'test')",
            "openerp.Tour.tours.website_test_uom")
