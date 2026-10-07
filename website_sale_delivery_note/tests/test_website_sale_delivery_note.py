# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase

from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_delivery_note.controllers.main import (
    WebsiteSaleDeliveryNote,
)


class TestWebsiteSaleDeliveryNote(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref(
            "website.default_website", raise_if_not_found=False
        ) or cls.env["website"].create({"name": "Delivery Note Test Website"})
        cls.partner = cls.env["res.partner"].create({"name": "Delivery Note Test"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "website_id": cls.website.id,
            }
        )

    def test_controller_saves_delivery_note(self):
        """The delivery note typed at the checkout is saved on the cart."""
        with MockRequest(self.env, website=self.website, sale_order_id=self.order.id):
            WebsiteSaleDeliveryNote().save_delivery_note(
                delivery_note="Leave at the back door"
            )
        self.assertEqual(self.order.delivery_note, "Leave at the back door")

    def test_delivery_note_carried_to_picking(self):
        """The delivery note is carried over to the delivery picking."""
        self.order.delivery_note = "Fragile"
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "partner_id": self.partner.id,
                "sale_id": self.order.id,
            }
        )
        self.assertEqual(picking.delivery_note, "Fragile")
