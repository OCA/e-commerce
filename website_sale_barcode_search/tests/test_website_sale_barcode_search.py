# Copyright 2026 OERP Canada - Helena Wong
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestWebsiteSaleBarcodeSearch(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Barcode searchable product",
                "sale_ok": True,
                "is_published": True,
                "barcode": "1234567890123",
                "list_price": 10.0,
            }
        )

    def test_product_search_fetches_barcode_matches(self):
        search_detail = self.env["product.template"]._search_get_detail(
            self.website,
            order="",
            options={
                "displayImage": False,
                "displayDescription": False,
                "displayExtraLink": False,
                "displayDetail": False,
            },
        )

        records, count = self.env["product.template"]._search_fetch(
            search_detail,
            self.product.barcode,
            limit=5,
            order="",
        )

        self.assertIn(self.product.product_tmpl_id, records)
        self.assertEqual(count, 1)
