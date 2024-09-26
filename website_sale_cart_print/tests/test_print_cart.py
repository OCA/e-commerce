#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import http
from contextlib import contextmanager

from odoo import Command
from odoo.http import Request, _generate_routing_rules
from odoo.tests.common import HttpCase, tagged

from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_cart_print.controllers.main import WebsiteSaleCartPrint


@tagged("post_install", "-at_install")
class WebsiteSalePrintCart(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = WebsiteSaleCartPrint()
        cls.user = cls.env.user
        cls.partner = cls.user.partner_id
        cls._setup_customer_checkout(cls.partner)
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "sale_ok": True,
                "website_published": True,
            }
        )
        cls.order = cls._setup_order(cls.partner, cls.product)
        cls.website = cls.env.ref("website.default_website")

        # Propagate routing for inherited endpoints,
        # otherwise our endpoint won't have any routing
        installed_modules = cls.env["ir.module.module"].search(
            [
                ("state", "=", "installed"),
            ],
        )
        installed_modules_names = set(installed_modules.mapped("name"))
        for _ in _generate_routing_rules(installed_modules_names, False):
            pass

    @classmethod
    def _setup_customer_checkout(cls, customer):
        """Fill anything is needed for `customer` for checkout."""
        customer.update(
            {
                "street": "Test Street",
                "city": "Test City",
                "country_id": cls.env.ref("base.be").id,
                "zip": "12345",
            }
        )
        return customer

    @classmethod
    def _setup_order(cls, partner, products):
        """Create order ready for checkout."""
        order = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                        }
                    )
                    for product in products
                ],
            }
        )
        return order

    def _assert_order_printed(self, response, order):
        """`response` contains the printed PDF of `order`."""
        # Response shape
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertIn("pdf", response.content_type)

        # Response content
        decoded_data = response.data.decode()
        partner = order.partner_id
        self.assertIn(partner.name, decoded_data)
        self.assertIn(order.name, decoded_data)

    @contextmanager
    def _patch_mock_request(self, *args, **kwargs):
        # core's mocked request does many things, but does not implement make_response
        # here we add it because is used when printing the order
        with MockRequest(*args, **kwargs) as mock_request:
            mock_request.make_response = Request(mock_request.httprequest).make_response
            yield mock_request

    def test_print_cart(self):
        """The order of the cart is printed when clicking on its button."""
        order = self.order
        with self._patch_mock_request(
            self.env,
            sale_order_id=order.id,
            website=self.website,
        ):
            response = self.controller.print_saleorder(
                cart_print="true",  # the controller is receiving "true", not True
            )
            self._assert_order_printed(response, order)

    def test_print_confirmed_order(self):
        """Check that cart is printed at the end of checkout."""
        controller = self.controller
        order = self.order
        with self._patch_mock_request(
            self.env,
            sale_order_id=order.id,
            website=self.website,
        ) as mock_request:
            self.assertFalse(mock_request.session.get("sale_last_order_id"))
            controller.confirm_order()
            self.assertEqual(mock_request.session.get("sale_last_order_id"), order.id)

            response = controller.print_saleorder()
            self._assert_order_printed(response, order)
