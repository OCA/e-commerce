# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class WebsiteSaleAssuranceRenderCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.product = cls.env["product.template"].create(
            {
                "name": "Assurance test product",
                "is_published": True,
                "type": "consu",
                "list_price": 99.0,
            }
        )
        cls.assurance = cls.env["website.sale.assurance"].create(
            {
                "name": "30-day money-back guarantee",
                "subtitle": "No questions asked",
                "icon": "fa-shield",
            }
        )

    def test_assurance_block_rendered_on_product_page(self):
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("o_wsale_assurance", response.text)
        self.assertIn("o_wsale_assurance-cols-4", response.text)
        self.assertIn("30-day money-back guarantee", response.text)
        self.assertIn("No questions asked", response.text)

    def test_icon_name_rendered(self):
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertIn("o_wsale_assurance-icon fa fa-shield", response.text)

    def test_image_icon_rendered(self):
        self.assurance.image = base64.b64encode(b"fake-png-bytes")
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertIn(
            f"/web/image/website.sale.assurance/{self.assurance.id}/image",
            response.text,
        )

    def test_default_terms_block_when_no_items(self):
        self.env["website.sale.assurance"].search([]).unlink()
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("o_translate_inline text-muted", response.text)
