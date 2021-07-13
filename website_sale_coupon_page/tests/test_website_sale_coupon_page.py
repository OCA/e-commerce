# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

from PIL import Image

from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        # Creation of generic test banner
        f = io.BytesIO()
        Image.new("RGB", (800, 500), "#FF0000").save(f, "JPEG")
        f.seek(0)
        image = base64.b64encode(f.read())
        self.promo_public = self.env["sale.coupon.program"].create(
            {
                "program_type": "promotion_program",
                "name": "Test 01",
                "is_published": True,
                "rule_partners_domain": "[]",
                "public_name": "10% discount",
                "image_1920": image,
            }
        )
        admin = self.env.ref("base.user_admin")
        self.promo_private = self.env["sale.coupon.program"].create(
            {
                "program_type": "promotion_program",
                "name": "Test 02",
                "is_published": True,
                "rule_partners_domain": "[['id', '=', %s]]" % admin.partner_id.id,
                "public_name": "10% discount just for admin",
            }
        )
        self.promo_not_published = self.env["sale.coupon.program"].create(
            {
                "program_type": "promotion_program",
                "name": "Test 03",
                "is_published": False,
                "rule_partners_domain": "[]",
            }
        )

    def test_ui_admin_user(self):
        """Test frontend tour with admin user."""
        self.start_tour(
            "/promotions", "website_sale_coupon_page_admin", login="admin",
        )

    def test_ui_portal_user(self):
        """Test frontend tour with demo user."""
        self.start_tour(
            "/promotions", "website_sale_coupon_page_portal", login="portal",
        )
