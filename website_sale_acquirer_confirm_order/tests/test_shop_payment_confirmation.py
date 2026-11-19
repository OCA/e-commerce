# Copyright 2026 Binhex - Edilio Escalona Almira
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.http import root
from odoo.tests import tagged

from odoo.addons.payment.tests.http_common import PaymentHttpCommon


@tagged("post_install", "-at_install")
class TestShopPaymentConfirmation(PaymentHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider.confirm_order = True
        product = cls.env["product.product"].create(
            {"name": "Test product", "list_price": 100}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [Command.create({"product_id": product.id})],
            }
        )

    def _open_confirmation_page(self):
        self._create_transaction(
            flow="redirect",
            sale_order_ids=[Command.set(self.order.ids)],
            state="pending",
        )
        session = self.authenticate(None, None)
        session["sale_last_order_id"] = self.order.id
        root.session_store.save(session)
        return self.url_open("/shop/confirmation")

    def test_confirmation_page_confirms_quotation(self):
        response = self._open_confirmation_page()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.state, "sale")

    def test_confirmation_page_with_cancelled_order(self):
        """Coming back to the confirmation page with a cancelled order in the
        session shows the page and leaves the order cancelled."""
        self.order._action_cancel()
        response = self._open_confirmation_page()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.state, "cancel")
