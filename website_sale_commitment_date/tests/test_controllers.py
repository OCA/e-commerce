# Copyright 2025 Binhex - Adasat Torres de León
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from freezegun import freeze_time

from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_commitment_date.controllers.main import (
    WebsiteSaleCommitmentDate,
)


@freeze_time("2025-01-09 15:00:00")
@tagged("post_install", "-at_install")
class TestWebsiteSaleCommitmentDateController(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.Controller = WebsiteSaleCommitmentDate()
        cls.DeliveryCarrier = cls.env["delivery.carrier"]
        cls.lang = cls.env["res.lang"]._lang_get(
            cls.env.context.get("lang", False) or cls.env.lang or cls.env.user.lang
        )

    def test01_website_sale_commitment_date(self):
        with MockRequest(self.env, website=self.website):
            order = self.website.sale_get_order(force_create=True)
            carrier_id = self.DeliveryCarrier.create(
                {
                    "name": "Test carrier Allow commitment date",
                    "allow_commitment_date": True,
                    "product_id": self.env.ref("product.product_product_4").id,
                }
            )
            order.carrier_id = carrier_id.id
            response = self.Controller.commitment_date()
            self.assertEqual(response["month"], 1)
            self.assertEqual(response["year"], 2025)
            self.assertTrue(response["weeks"])
            self.assertEqual(
                response["start"], date(2025, 1, 1).strftime(self.lang.date_format)
            )
            response = self.Controller.commitment_date(
                **{"action": "next", "start": response["start"]}
            )
            self.assertEqual(response["month"], 2)
            self.assertEqual(response["year"], 2025)
            self.assertEqual(
                response["start"], date(2025, 2, 1).strftime(self.lang.date_format)
            )
            response = self.Controller.commitment_date(
                **{"action": "next", "start": response["start"]}
            )
            self.assertEqual(response["month"], 3)
            self.assertEqual(response["year"], 2025)
            self.assertEqual(
                response["start"], date(2025, 3, 1).strftime(self.lang.date_format)
            )
            response = self.Controller.commitment_date(
                **{"action": "prev", "start": response["start"]}
            )
            self.assertEqual(response["month"], 2)
            self.assertEqual(response["year"], 2025)
            self.assertEqual(
                response["start"], date(2025, 2, 1).strftime(self.lang.date_format)
            )
            response = self.Controller.commitment_date(
                **{"action": "prev", "start": response["start"]}
            )
            self.assertEqual(response["month"], 1)
            self.assertEqual(response["year"], 2025)
            self.assertEqual(
                response["start"],
                date(2025, 1, 1).strftime(self.lang.date_format),
            )

    def test02_website_update_commitment_date(self):
        with MockRequest(self.env, website=self.website):
            order = self.website.sale_get_order(force_create=True)
            order.carrier_id = self.DeliveryCarrier.create(
                {
                    "name": "Test carrier Allow commitment date",
                    "allow_commitment_date": True,
                    "product_id": self.env.ref("product.product_product_4").id,
                }
            ).id
            response = self.Controller.update_commitment_date(
                **{"date": date(2025, 1, 10).strftime(self.lang.date_format)}
            )
            self.assertTrue(response["success"])
            self.assertEqual(
                response["date"], date(2025, 1, 10).strftime(self.lang.date_format)
            )
            self.assertEqual(
                order.commitment_date.strftime(self.lang.date_format),
                date(2025, 1, 10).strftime(self.lang.date_format),
            )
