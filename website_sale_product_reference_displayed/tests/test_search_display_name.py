# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSearchDisplayName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].search([], limit=1)
        cls.view = cls.env.ref(
            "website_sale_product_reference_displayed.search_display_name"
        )
        cls.options = {
            "displayImage": False,
            "displayDescription": False,
            "displayExtraLink": False,
            "displayDetail": False,
        }

    def _get_detail(self):
        return self.env["product.template"]._search_get_detail(
            self.website, "", self.options
        )

    def test_search_detail_uses_display_name_when_active(self):
        self.view.active = True
        self.env.registry.clear_cache()
        detail = self._get_detail()
        self.assertEqual(detail["mapping"]["name"]["name"], "display_name")
        self.assertIn("display_name", detail["fetch_fields"])

    def test_search_detail_keeps_name_when_inactive(self):
        self.view.active = False
        self.env.registry.clear_cache()
        detail = self._get_detail()
        self.assertEqual(detail["mapping"]["name"]["name"], "name")
        self.assertNotIn("display_name", detail["fetch_fields"])
