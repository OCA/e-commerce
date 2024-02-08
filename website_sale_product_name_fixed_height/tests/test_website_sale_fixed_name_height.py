# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestWebsiteSaleFixedNameHeight(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.website = cls.env["website"].browse(1)

    def test_change_row_count_1(self):
        """
        Test changing the row count in the description in settings.
        """
        config_obj = self.env["res.config.settings"]
        config = config_obj.create({"row_count": 3})
        config.execute()
        self.assertEqual(self.website.row_count, 3, msg="Row count must be equal 3")

    def test_change_row_count_2(self):
        """
        Test changing the row count in the description in settings.
        """
        with self.assertRaises(ValidationError):
            config_obj = self.env["res.config.settings"]
            config = config_obj.create({"row_count": 0})
            config.execute()
        self.assertEqual(self.website.row_count, 1, msg="Row count must be equal 1")
