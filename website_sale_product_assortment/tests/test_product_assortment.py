from odoo.tests import SavepointCase


class TestProductAssortment(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.assortment_model = cls.env["ir.filters"]
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product 1",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
            }
        )

    def get_product_combination_info(self):
        return (
            self.product.with_user(self.admin_user)
            .with_context(website_id=1)
            ._get_combination_info(product_id=self.product.id)
        )

    def test_combination_info_no_assortment(self):
        info = self.get_product_combination_info()
        self.assertFalse(info.get("product_avoid_purchase"))
        self.assertFalse(info.get("product_assortment_type"))
        self.assertFalse(info.get("message_unavailable"))
        self.assertFalse(info.get("assortment_information"))

    def test_combination_info_assortment_includes_product(self):
        self.assortment_model.create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("type", "=", "consu")],
                "partner_domain": [("id", "=", self.admin_user.partner_id.id)],
                "website_availability": "no_show",
            }
        )

        info = self.get_product_combination_info()
        self.assertFalse(info.get("product_avoid_purchase"))
        self.assertFalse(info.get("product_assortment_type"))
        self.assertFalse(info.get("message_unavailable"))
        self.assertFalse(info.get("assortment_information"))

    def test_combination_info_assortment_excludes_product_no_show(self):
        self.assortment_model.create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("type", "=", "service")],
                "partner_domain": [("id", "=", self.admin_user.partner_id.id)],
                "website_availability": "no_show",
            }
        )

        info = self.get_product_combination_info()
        self.assertEqual(info.get("product_avoid_purchase"), True)
        self.assertEqual(info.get("product_assortment_type"), "no_show")
        self.assertFalse(info.get("message_unavailable"))
        self.assertFalse(info.get("assortment_information"))

    def test_combination_info_assortment_excludes_product_no_purchase(self):
        message_unavailable = "<p>My Message Unavailable</p>"
        assortment_information = "<p>My Assortment Info</p>"
        self.assortment_model.create(
            {
                "name": "Test Assortment",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("type", "=", "service")],
                "partner_domain": [("id", "=", self.admin_user.partner_id.id)],
                "website_availability": "no_purchase",
                "message_unavailable": message_unavailable,
                "assortment_information": assortment_information,
            }
        )

        info = self.get_product_combination_info()
        self.assertEqual(info.get("product_avoid_purchase"), True)
        self.assertEqual(info.get("product_assortment_type"), "no_purchase")
        self.assertEqual(info.get("message_unavailable"), message_unavailable)
        self.assertEqual(info.get("assortment_information"), assortment_information)

    def test_combination_info_multiple_assortment_exclude_product(self):
        message_unavailable = "<p>My Message Unavailable</p>"
        assortment_information = "<p>My Assortment Info</p>"
        self.assortment_model.create(
            {
                "name": "Test Assortment 1",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("id", "=", 1)],
                "partner_domain": [("id", "=", self.admin_user.partner_id.id)],
                "website_availability": "no_show",
            }
        )
        self.assortment_model.create(
            {
                "name": "Test Assortment 2",
                "model_id": "product.product",
                "is_assortment": True,
                "domain": [("type", "=", "service")],
                "partner_domain": [("id", "=", self.admin_user.partner_id.id)],
                "website_availability": "no_purchase",
                "message_unavailable": message_unavailable,
                "assortment_information": assortment_information,
            }
        )

        info = self.get_product_combination_info()
        self.assertEqual(info.get("product_avoid_purchase"), True)
        self.assertEqual(info.get("product_assortment_type"), "no_show")
        self.assertFalse(info.get("message_unavailable"))
        self.assertFalse(info.get("assortment_information"))
