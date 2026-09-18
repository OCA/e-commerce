# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class _FakeRequest:
    """Minimal stand-in for the website ``request`` used by the base methods."""

    def __init__(self, env):
        self.session = {}
        self.fiscal_position = env["account.fiscal.position"]
        self.pricelist = env["product.pricelist"]
        self.geoip = SimpleNamespace(country_code="")


class TestWebsiteSalePartnerSaleContact(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].search([], limit=1)
        cls.company_partner = cls.env["res.partner"].create(
            {"name": "Acme Corp", "is_company": True}
        )
        cls.contact = cls.env["res.partner"].create(
            {
                "name": "John Buyer",
                "is_company": False,
                "parent_id": cls.company_partner.id,
            }
        )
        cls.individual = cls.env["res.partner"].create(
            {
                "name": "Jane Solo",
                "is_company": False,
                "company_name": "Solo Trading Ltd",
            }
        )

    def setUp(self):
        super().setUp()
        fake = _FakeRequest(self.env)
        for module in ("website", "sale_order"):
            patcher = patch(f"odoo.addons.website_sale.models.{module}.request", fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_prepare_sale_order_values_remaps_contact(self):
        values = self.website._prepare_sale_order_values(self.contact)
        self.assertEqual(values["partner_id"], self.company_partner.id)
        self.assertEqual(values["sale_contact_partner_id"], self.contact.id)

    def test_prepare_sale_order_values_creates_company_from_name(self):
        values = self.website._prepare_sale_order_values(self.individual)
        company = self.env["res.partner"].browse(values["partner_id"])
        self.assertEqual(company.name, "Solo Trading Ltd")
        self.assertTrue(company.is_company)
        self.assertEqual(self.individual.parent_id, company)
        self.assertEqual(values["sale_contact_partner_id"], self.individual.id)

    def test_update_address_remaps_only_customer(self):
        order = self.env["sale.order"].create(
            {"partner_id": self.company_partner.id, "website_id": self.website.id}
        )
        order._update_address(
            self.contact.id, ["partner_id", "partner_invoice_id", "partner_shipping_id"]
        )
        self.assertEqual(order.partner_id, self.company_partner)
        self.assertEqual(order.sale_contact_partner_id, self.contact)
        self.assertEqual(order.partner_invoice_id, self.contact)
        self.assertEqual(order.partner_shipping_id, self.contact)
