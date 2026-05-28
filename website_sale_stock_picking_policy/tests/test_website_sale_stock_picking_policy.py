# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import Mock, patch

from odoo import Command, fields
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.website_sale_stock_picking_policy.controllers.main import (
    WebsiteSalePickingPolicy,
)


class TestWebsiteSaleStockPickingPolicy(BaseCommon):
    REQUEST_PATCH_PATH = (
        "odoo.addons.website_sale_stock_picking_policy.controllers.main.request"
    )
    SUPER_PREPARE_PATCH_PATH = (
        "odoo.addons.website_sale_stock_picking_policy.controllers.main."
        "WebsiteSale._prepare_checkout_page_values"
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Policy Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Policy Test Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        cls.controller = WebsiteSalePickingPolicy()

    def _mock_request(self, *, cart):
        return patch(self.REQUEST_PATCH_PATH, new=Mock(env=self.env, cart=cart))

    def _mock_request_env_only(self):
        return patch(self.REQUEST_PATCH_PATH, new=Mock(env=self.env))

    def test_prepare_checkout_page_values_adds_picking_policy_selection(self):
        """Controller should inject picking policy options into checkout values."""
        expected_selection = dict(
            self.order._fields["picking_policy"]._description_selection(self.env)
        )

        with (
            self._mock_request_env_only(),
            patch(self.SUPER_PREPARE_PATCH_PATH, return_value={"base_value": True}),
        ):
            result = self.controller._prepare_checkout_page_values(self.order)

        self.assertTrue(result["base_value"])
        self.assertEqual(result["picking_policy_selection_values"], expected_selection)

    def test_update_picking_policy_without_expected_date(self):
        """If the order has no expected date, the endpoint should return False."""
        order = Mock(expected_date=False)

        with self._mock_request(cart=order):
            result = self.controller.update_picking_policy("direct")

        order.write.assert_called_once_with({"picking_policy": "direct"})
        self.assertFalse(result["expected_date"])

    def test_update_picking_policy_with_expected_date(self):
        """If expected_date exists, endpoint should return it as a date string."""
        self.order.expected_date = fields.Date.today()
        self.order.picking_policy = "one"
        expected_date = fields.Date.to_string(
            fields.Date.context_today(self.order, self.order.expected_date)
        )

        with self._mock_request(cart=self.order):
            result = self.controller.update_picking_policy("direct")

        self.assertEqual(self.order.picking_policy, "direct")
        self.assertEqual(result["expected_date"], expected_date)

    def test_update_picking_policy_without_cart_raises(self):
        """A missing cart should raise a user-facing error."""
        with self._mock_request(cart=False):
            with self.assertRaises(UserError):
                self.controller.update_picking_policy("one")
