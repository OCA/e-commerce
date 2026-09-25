# Copyright 2026 ADHOC SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestWebsiteSaleCarrierAutoAssign(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.company.carrier_on_create = True

        cls.partner_carrier = cls._prepare_carrier(
            cls._create_product(name="Partner Default Carrier"),
            name="Partner Default Carrier",
            delivery_type="fixed",
            fixed_price=1000.0,
        )

        cls.web_carrier = cls._prepare_carrier(
            cls._create_product(name="Web Selected Carrier"),
            name="Web Selected Carrier",
            delivery_type="fixed",
            fixed_price=0.0,
        )

        cls.partner.property_delivery_carrier_id = cls.partner_carrier

    def test_is_auto_set_carrier_disabled_for_website_order(self):
        """_is_auto_set_carrier_on_create must return False for website orders
        so the OCA auto-assign is never triggered during create/write."""
        order = self._create_so()
        self.assertFalse(
            order._is_auto_set_carrier_on_create(),
            "OCA carrier auto-assign should be disabled for website orders.",
        )

    def test_is_auto_set_carrier_enabled_for_backend_order(self):
        """For orders without website_id the OCA logic must still run normally.

        The order must have at least one non-service product: the OCA gate
        checks `not is_all_service`, which is True for empty orders (vacuous
        truth of `all([])`) and would mask the website_id difference.
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        self.assertTrue(
            order._is_auto_set_carrier_on_create(),
            "OCA carrier auto-assign should remain active for backend orders.",
        )

    def test_no_duplicate_delivery_line_after_set_delivery_method(self):
        """Creating a website order with a product and then setting a delivery
        method must result in exactly one delivery line (not two).

        Without the glue module, OCA's write override would add a line for
        partner_carrier while _set_delivery_method adds one for web_carrier,
        giving two lines and a singleton error in order_2_return_dict.
        """
        order = self._create_so()

        order._set_delivery_method(self.web_carrier)

        delivery_lines = order.order_line.filtered("is_delivery")
        self.assertEqual(
            len(delivery_lines),
            1,
            "There must be exactly one delivery line after _set_delivery_method. "
            f"Got {len(delivery_lines)}: {delivery_lines.mapped('name')}",
        )
        self.assertEqual(
            delivery_lines.product_id,
            self.web_carrier.product_id,
            "The single delivery line must correspond to the web-selected carrier.",
        )
