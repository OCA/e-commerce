# Copyright 2020-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest


class TestWebsiteSaleAffiliateProductRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestWebsiteSaleAffiliateProductRestriction, cls).setUpClass()
        seq = cls.env.ref("website_sale_affiliate.request_sequence")
        cls.affiliate = cls.env["sale.affiliate"].create(
            {
                "name": "my affiliate",
                "company_id": cls.env.ref("base.main_company").id,
                "sequence_id": seq.id,
                "valid_hours": 24,
                "valid_sales": 100,
            }
        )

        cls.pt1 = cls.env.ref("product.product_product_1").product_tmpl_id
        cls.pt2 = cls.env.ref("product.product_product_2").product_tmpl_id
        cls.pt3 = cls.env.ref("product.product_product_3").product_tmpl_id

    def create_affiliate_req(self, create_date=None):
        req = self.env["sale.affiliate.request"].create(
            {
                "name": "test affiliate request",
                "affiliate_id": self.affiliate.id,
                "date": fields.Datetime.now(),
                "ip": "127.0.0.1",
                "referrer": "https://commown.coop",
                "user_agent": "firefox",
                "accept_language": "fr",
            }
        )
        if create_date is not None:
            req.create_date = create_date
        return req

    def create_sale(self, products=None, state="sent", create_date=None):
        partner_1 = self.env.ref("base.res_partner_1")
        if products is None:
            products = [self.env.ref("product.product_product_1"), 1]
        data = {
            "partner_id": partner_1.id,
            "partner_invoice_id": partner_1.id,
            "partner_shipping_id": partner_1.id,
            "pricelist_id": self.env.ref("product.list0").id,
            "state": state,
            "order_line": [],
        }
        for product, qty in products:
            data["order_line"].append(
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                        "price_unit": product.list_price,
                    },
                )
            )
        sale = self.env["sale.order"].create(data)
        if create_date is not None:
            sale.create_date = create_date
        return sale

    def test_sale_order_without_product_restriction(self):
        with MockRequest(self.env) as mock_request:
            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            self.create_sale([(self.pt1, 1), (self.pt2, 1)], "sent")

            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            self.create_sale([(self.pt2, 1), (self.pt3, 1)], "draft")
            self.create_sale([(self.pt3, 1)], "sent")
            self.create_sale([(self.pt1, 1)], "sent")
            self.create_sale([(self.pt2, 1)], "sent")

            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            mock_request.session["affiliate_request"] = self.create_affiliate_req().id

        self.assertAlmostEqual(self.affiliate.sales_per_request, 1)
        self.assertAlmostEqual(self.affiliate.conversion_rate, 0.5)

    def test_sale_order_with_product_restriction(self):
        self.affiliate.restriction_product_tmpl_ids |= self.pt2 | self.pt3

        with MockRequest(self.env) as mock_request:
            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            self.create_sale([(self.pt1, 1)], "sent")

            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            self.create_sale([(self.pt1, 1), (self.pt3, 1)], "sent")
            self.create_sale([(self.pt2, 1)], "sent")

            mock_request.session["affiliate_request"] = self.create_affiliate_req().id
            mock_request.session["affiliate_request"] = self.create_affiliate_req().id

        self.assertEqual(self.affiliate.sales_per_request, 0.5)
        self.assertAlmostEqual(self.affiliate.conversion_rate, 0.25)
