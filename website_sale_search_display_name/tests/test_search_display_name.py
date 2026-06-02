# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSearchDisplayName(TransactionCase):
    def test_search_detail_uses_display_name(self):
        website = self.env["website"].search([], limit=1)
        options = {
            "displayImage": False,
            "displayDescription": False,
            "displayExtraLink": False,
            "displayDetail": False,
        }
        detail = self.env["product.template"]._search_get_detail(website, "", options)
        self.assertEqual(detail["mapping"]["name"]["name"], "display_name")
        self.assertIn("display_name", detail["fetch_fields"])
