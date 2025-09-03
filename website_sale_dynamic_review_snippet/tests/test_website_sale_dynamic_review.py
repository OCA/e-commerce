from odoo.tests import HttpCase, tagged

from odoo.addons.mail.tests.common import mail_new_test_user
from odoo.addons.website_sale_dynamic_review_snippet.controllers.main import (
    CustomerReview,
)


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = CustomerReview()
        cls.user_admin = cls.env.ref("base.user_admin")
        cls.company_admin = cls.user_admin.company_id
        cls.user_portal = mail_new_test_user(
            cls.env,
            login="portal_test",
            groups="base.group_portal",
            company_id=cls.company_admin.id,
            name="Chell Gladys",
            notification_type="email",
        )
        cls.partner_portal = cls.user_portal.partner_id
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "is_published": True,
            }
        )
        cls.message = cls.product.with_user(cls.user_portal).message_post(
            body="Not bad",
            message_type="comment",
            rating_value=3,
            subtype_xmlid="mail.mt_comment",
        )
        cls.website = cls.env["website"].browse(1)

    def test_admin_tour(self):
        self.start_tour(
            self.env["website"].get_client_action_url("/"),
            "dynamic_review",
            login="admin",
            step_delay=2000,
        )
