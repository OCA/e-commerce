# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from urllib.parse import parse_qs, urlsplit

from odoo.tests import HttpCase, tagged

from odoo.addons.website.models.mixins import WebsitePublishedMultiMixin


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
            {"name": "web0", "domain": cls.website0_host, "sequence": 10}
        )
        cls.website1 = cls.env["website"].create(
            {"name": "web1", "domain": cls.website1_host, "sequence": 20}
        )
        cls.website2 = cls.env["website"].create(
            {"name": "web2", "domain": cls.website2_host, "sequence": 30}
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

    def _assert_website_action(self, record, website):
        action = record.open_website_url()
        if website.domain:
            self.assertEqual(action["type"], "ir.actions.act_url")
            self.assertEqual(action["target"], "self")
            parsed = urlsplit(action["url"])
            self.assertEqual(parsed.netloc, urlsplit(website.domain).netloc)
            self.assertEqual(parsed.path, "/odoo/action-website.website_preview")
            self.assertEqual(
                parse_qs(parsed.query),
                {"path": [record.website_url], "website_id": [str(website.id)]},
            )
        else:
            self.assertEqual(action["type"], "ir.actions.client")
            self.assertEqual(action["tag"], "website_preview")
            self.assertEqual(
                action["params"],
                {
                    "path": record.website_url,
                    "enable_editor": False,
                    "website_id": website.id,
                },
            )

    def test_open_single_website(self):
        self.product_template.website_ids = self.website1
        self._assert_website_action(self.product_template, self.website1)

    def test_open_multiple_websites_ignores_stored_website(self):
        product = self.product_template
        # Reproduce assigning one website, then adding earlier websites.
        product.website_ids = self.website2
        product.website_ids = self.website2 + self.website1 + self.website0
        product.website_id = self.website2
        self.assertEqual(product.website_id, self.website2)
        self._assert_website_action(product, self.website0)
        # Sequence changes must be reflected without recomputing website_id.
        self.website1.sequence = 5
        self._assert_website_action(product, self.website1)
        self.assertEqual(product.website_id, self.website2)

    def test_open_context_website(self):
        product = self.product_template
        product.website_ids = self.website0 + self.website2
        self._assert_website_action(
            product.with_context(website_id=self.website2.id), self.website2
        )
        self._assert_website_action(
            product.with_context(website_id=self.website1.id), self.website0
        )

    def test_open_websites_with_equal_sequences(self):
        self.website1.sequence = self.website0.sequence
        self.product_template.website_ids = self.website1 + self.website0
        self.product_template.website_id = self.website1
        self._assert_website_action(self.product_template, self.website0)

    def test_open_website_without_domain(self):
        self.website1.domain = False
        self.product_template.website_ids = self.website1
        self._assert_website_action(self.product_template, self.website1)

    def test_open_without_websites_uses_standard_action(self):
        for website in (self.website0, self.website1):
            product = self.product_template.with_context(website_id=website.id)
            self.assertEqual(
                product.open_website_url(),
                WebsitePublishedMultiMixin.open_website_url(product),
            )
            variant = product.product_variant_id
            action = variant.open_website_url()
            expected = WebsitePublishedMultiMixin.open_website_url(product)
            expected["url"] = variant.website_url
            self.assertEqual(action, expected)

    def test_open_variant_preserves_website_and_attributes(self):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Navigation attribute",
                "value_ids": [(0, 0, {"name": "First"}), (0, 0, {"name": "Second"})],
            }
        )
        product = self.product_template
        product.attribute_line_ids = [
            (
                0,
                0,
                {
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, attribute.value_ids.ids)],
                },
            )
        ]
        product.website_ids = self.website0 + self.website1
        variant = product.product_variant_ids[0].with_context(
            website_id=self.website1.id
        )
        self.assertIn("attribute_values=", variant.website_url)
        self._assert_website_action(variant, self.website1)
        self.website1.domain = False
        self._assert_website_action(variant, self.website1)

    def test_navigation_preserves_publication_and_visibility(self):
        product = self.product_template
        product.website_ids = self.website1 + self.website2
        product.is_published = False
        self._assert_website_action(product, self.website1)
        self.assertFalse(product.is_published)
        for website in (self.website0, self.website1, self.website2):
            self.assertFalse(
                product.with_context(website_id=website.id).website_published
            )
        product.is_published = True
        self._assert_website_action(product, self.website1)
        self.assertEqual(product.website_ids, self.website1 + self.website2)
        for website in (self.website0, self.website1, self.website2):
            allowed = website != self.website0
            self.assertEqual(
                product.with_context(website_id=website.id).website_published, allowed
            )
            self.assertEqual(
                product.can_access_from_current_website(website.id), allowed
            )
