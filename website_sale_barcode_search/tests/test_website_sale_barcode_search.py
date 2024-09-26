# Copyright 2025 Sergi Biosca - Studio73
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import HttpCase


class WebsiteSale(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].create({"name": "Test Website"})
        cls.detail = cls.env["product.template"]._search_get_detail(
            cls.website,
            order=None,
            options={
                "displayImage": False,
                "displayDescription": False,
                "displayExtraLink": False,
                "displayDetail": False,
            },
        )

    def test_website_trigram(self):
        self.assertEqual(self.detail["search_fields"][-1], "barcode")
        trigram_enumerate = self.website._trigram_enumerate_words(
            search_details=[
                {
                    "model": "product.template",
                    "search_fields": ["name", "description", "barcode"],
                }
            ],
            search="Test",
            limit=10,
        )
        self.assertTrue(trigram_enumerate)
