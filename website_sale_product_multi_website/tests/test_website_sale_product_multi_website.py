# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductMultiWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create multiple websites
        cls.website0_host = "web0.local"
        cls.website1_host = "web1.local"
        cls.website2_host = "web2.local"
        cls.website0 = cls.env["website"].create(
            {"name": "web0", "domain": cls.website0_host}
        )
        cls.website1 = cls.env["website"].create(
            {"name": "web1", "domain": cls.website1_host}
        )
        cls.website2 = cls.env["website"].create(
            {"name": "web2", "domain": cls.website2_host}
        )

        # Create a product template
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product Multi Website",
                "is_published": True,
                "list_price": 750,
                "sequence": 10,
            }
        )

    def test_01_product_without_websites_is_available_on_all_websites(self):
        # Check that a product without website_ids is available on all websites
        for website in (self.website0, self.website1, self.website2):
            product = self.product_template.with_context(website_id=website.id)
            self.assertTrue(
                product.website_published,
            )
            self.assertTrue(
                product.can_access_from_current_website(website_id=website.id)
            )

    def test_02_product_is_only_available_on_assigned_websites(self):
        # Assign the product to only one website
        self.product_template.website_ids = [(6, 0, self.website1.ids)]
        # Check that the product is only available on the assigned website
        self.assertTrue(
            self.product_template.can_access_from_current_website(
                website_id=self.website1.id
            )
        )
        self.assertFalse(
            self.product_template.can_access_from_current_website(
                website_id=self.website0.id
            )
        )
        self.assertFalse(
            self.product_template.can_access_from_current_website(
                website_id=self.website2.id
            )
        )

    def test_03_product_is_visible_only_on_assigned_website_shop(self):
        self.product_template.website_ids = self.website1
        product_url = self.product_template.website_url
        # Check that the product is listed on the assigned website
        response = self.url_open(
            "/shop?search=Test+Product+Multi+Website",
            headers={"Host": self.website1_host},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(product_url, response.text)
        # Check that the product is not listed on non-assigned websites
        for host in (self.website0_host, self.website2_host):
            response = self.url_open(
                "/shop?search=Test+Product+Multi+Website",
                headers={"Host": host},
            )
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(product_url, response.text)

    def test_04_website_ids_are_preserved_when_multiple_websites_are_assigned(self):
        self.product_template.website_ids = self.website1 + self.website2
        self.assertEqual(self.product_template.website_id, self.website1)
        self.assertEqual(
            self.product_template.website_ids, self.website1 + self.website2
        )

    def test_05_inverse_adds_website_without_replacing_existing_websites(self):
        self.product_template.website_ids = self.website1 + self.website2
        self.product_template.website_id = self.website0
        self.assertEqual(
            set(self.product_template.website_ids.ids),
            set((self.website0 + self.website1 + self.website2).ids),
        )

    def test_06_inverse_does_not_duplicate_existing_website(self):
        self.product_template.website_ids = self.website1 + self.website2
        self.product_template.website_id = self.website1
        self.assertEqual(
            set(self.product_template.website_ids.ids),
            set((self.website1 + self.website2).ids),
        )

    def test_07_accessory_domain_does_not_raise_for_public_user(self):
        # Regression test: website_domain()'s website_ids condition used to be
        # evaluated in-memory (filtered_domain) by _get_website_accessory_product,
        # which raised an AccessError for the public user instead of silently
        # filtering out the accessory it can't read (unpublished).
        published_accessory = self.env["product.template"].create(
            {"name": "Published accessory", "is_published": True, "list_price": 5}
        )
        unpublished_accessory = self.env["product.template"].create(
            {"name": "Unpublished accessory", "is_published": False, "list_price": 5}
        )
        self.product_template.accessory_product_ids = (
            published_accessory.product_variant_ids
            + unpublished_accessory.product_variant_ids
        )
        accessories = self.product_template.with_user(
            self.env.ref("base.public_user")
        )._get_website_accessory_product()
        self.assertEqual(accessories, published_accessory.product_variant_ids)
