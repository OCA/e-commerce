from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Seed a product review so the dynamic review snippet has data to fetch.
        # Post as the test user (admin): portal users cannot create mail.message
        # on product.template via ORM (no read access), same pattern as
        # website_sale.tests.test_website_sale_product_page.
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "is_published": True,
            }
        )
        cls.message = cls.product.message_post(
            body="Not bad",
            message_type="comment",
            rating_value="3",
            subtype_xmlid="mail.mt_comment",
        )

    def test_admin_tour(self):
        self.start_tour(
            self.env["website"].get_client_action_url("/"),
            "dynamic_review",
            login="admin",
            step_delay=2000,
        )
