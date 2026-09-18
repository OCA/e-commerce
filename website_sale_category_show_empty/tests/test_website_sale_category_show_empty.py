# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleCategoryShowEmpty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.public_user = cls.env.ref("base.public_user")
        cls.category = cls.env["product.public.category"].create(
            {"name": "Empty category"}
        )
        cls.child = cls.env["product.public.category"].create(
            {"name": "Empty child category", "parent_id": cls.category.id}
        )

    def _read_as_public(self, category):
        category.with_user(self.public_user).check_access("read")

    def test_01_empty_category_is_hidden(self):
        """Without the flag, the core rule keeps the category unreadable."""
        with self.assertRaises(AccessError):
            self._read_as_public(self.category)

    def test_02_flag_makes_category_readable(self):
        self.category.show_when_empty = True
        self._read_as_public(self.category)

    def test_03_flag_does_not_leak_to_siblings(self):
        """The flag widens access for its own record only."""
        self.category.show_when_empty = True
        with self.assertRaises(AccessError):
            self._read_as_public(self.child)

    def test_04_category_with_published_product_stays_readable(self):
        """The core rule keeps working for categories that do hold products."""
        self.env["product.template"].create(
            {
                "name": "Published product",
                "is_published": True,
                "public_categ_ids": [(6, 0, self.child.ids)],
            }
        )
        self._read_as_public(self.child)
        self._read_as_public(self.category)
