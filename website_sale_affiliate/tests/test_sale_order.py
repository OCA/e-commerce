# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from mock import patch

from ..models.sale_affiliate_request import AffiliateRequest
from .common import SaleCase


class SaleOrderCase(SaleCase):
    def setUp(self):
        super(SaleOrderCase, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")
        self.sale_order_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.demo_product.name,
                        "product_id": self.demo_product.id,
                        "product_uom_qty": 2,
                        "product_uom": self.demo_product.uom_id.id,
                        "price_unit": self.demo_product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
        }

    @patch.object(AffiliateRequest, "current_qualified")
    def test_create_calls_current_qualified(self, current_qualified_mock):
        """Calls current_qualified() on sale.affiliate.request model"""
        current_qualified_mock.return_value = None
        self.env["sale.order"].create(self.sale_order_vals)
        current_qualified_mock.assert_called_once_with()

    @patch.object(AffiliateRequest, "current_qualified")
    def test_create_adds_none(self, current_qualified_mock):
        """Sets affiliate_request_id to False when no current qualified
        affiliate request"""
        current_qualified_mock.return_value = None
        sale_order = self.env["sale.order"].create(self.sale_order_vals)
        self.assertTrue(sale_order.exists(), "Sale order not created")
        self.assertFalse(
            sale_order.affiliate_request_id,
            "Sale order not created properly",
        )

    @patch.object(AffiliateRequest, "current_qualified")
    def test_create_adds_affiliate_request_id(self, current_qualified_mock):
        """Adds id of qualified affiliate request to sale order"""
        current_qualified_mock.return_value = self.demo_request
        sale_order = self.env["sale.order"].create(self.sale_order_vals)
        self.assertTrue(sale_order.exists(), "Sale order not created")
        self.assertEqual(
            sale_order.affiliate_request_id,
            self.demo_request,
            "Request ID not added to sale order",
        )
