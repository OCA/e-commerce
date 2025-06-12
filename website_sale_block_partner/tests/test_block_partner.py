# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBlockPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.partner_demo")
        cls.env["account.journal"].create(
            {
                "name": "Test Journal",
                "code": "TSTJ",
                "type": "general",
            }
        )
        cls.partner.blacklist = True

    def test_sale_order_blacklisted_partner(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(
            "%s is marked as blacklisted" % self.partner.name,
            sale_order.partner_blacklist_warning,
        )
        self.partner.blacklist = False
        self.assertEqual(sale_order.partner_blacklist_warning, "")

    def test_invoice_blacklisted_partner(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(
            "%s is marked as blacklisted" % self.partner.name,
            invoice.partner_blacklist_warning,
        )
        self.partner.blacklist = False
        self.assertEqual(invoice.partner_blacklist_warning, "")
