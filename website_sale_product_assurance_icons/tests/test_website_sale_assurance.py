# Copyright 2026 Domatix (https://www.domatix.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestWebsiteSaleAssurance(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website1 = cls.env.ref("website.default_website")
        cls.website2 = cls.env["website"].create({"name": "Test Website"})
        cls.Assurance = cls.env["website.sale.assurance"]

    def test_global_item_is_returned_for_every_website(self):
        item = self.Assurance.create({"name": "Free shipping"})
        self.assertIn(item, self.website1._get_assurance_records())
        self.assertIn(item, self.website2._get_assurance_records())

    def test_website_specific_item_is_returned_only_for_its_website(self):
        item = self.Assurance.create(
            {"name": "Local pickup", "website_id": self.website1.id}
        )
        self.assertIn(item, self.website1._get_assurance_records())
        self.assertNotIn(item, self.website2._get_assurance_records())

    def test_inactive_items_are_excluded(self):
        item = self.Assurance.create({"name": "Old offer", "active": False})
        self.assertNotIn(item, self.website1._get_assurance_records())

    def test_records_are_sorted_by_sequence(self):
        first = self.Assurance.create({"name": "Last", "sequence": 20})
        second = self.Assurance.create({"name": "First", "sequence": 10})
        records = self.website1._get_assurance_records()
        self.assertLess(records.ids.index(second.id), records.ids.index(first.id))

    def test_internal_user_can_read_records(self):
        user = self.env["res.users"].create(
            {
                "name": "Shop Editor",
                "login": "shop_editor_assurance",
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        self.Assurance.create({"name": "Free shipping"})
        records = self.Assurance.with_user(user).search([])
        self.assertEqual(len(records), 1)

    def test_config_wizard_updates_website_columns(self):
        self.website1.assurance_columns = "4"
        wizard = self.env["website.sale.assurance.config"].create(
            {"website_id": self.website1.id}
        )
        wizard.assurance_columns = "2"
        self.assertEqual(self.website1.assurance_columns, "2")
