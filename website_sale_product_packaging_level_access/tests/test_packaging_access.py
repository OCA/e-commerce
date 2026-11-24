# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError

from odoo.addons.base.tests.common import BaseCommon


class ProductPackagingAccessTest(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
            }
        )
        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Box 1",
                "product_id": cls.product.id,
            }
        )
        cls.packaging_level = cls.env["product.packaging.level"].search(
            [("is_default", "=", True)], limit=1
        )
        cls.user_public = cls.env["res.users"].create(
            {
                "name": "Public user",
                "login": "pub_user",
            }
        )
        cls.user_no_groups = cls.env["res.users"].create(
            {"name": "User without group", "login": "user_no_group"}
        )
        cls.user_no_groups.groups_id = False
        cls.user_public.groups_id = cls.env.ref("base.group_public")

    def test_packaging_access(self):
        name = self.packaging.with_user(self.user_public).name
        self.assertEqual(
            "Box 1",
            name,
        )
        name = self.packaging.with_user(self.user_public).name
        self.assertEqual(
            "Box 1",
            name,
        )

    def test_packaging_no_access(self):
        name = False
        with self.assertRaises(AccessError):
            name = self.packaging.with_user(self.user_no_groups).name
        self.assertFalse(name)
