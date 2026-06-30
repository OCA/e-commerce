# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon


@tagged("post_install", "-at_install")
class TestWebsiteSaleTaxSelection(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_partner = cls.env["res.partner"].create(
            {"name": "Website Tax Selection Company", "is_company": True}
        )
        cls.contact_partner = cls.env["res.partner"].create(
            {
                "name": "Website Tax Selection Contact",
                "parent_id": cls.company_partner.id,
                "type": "contact",
            }
        )
        cls.website_user = cls.env["res.users"].create(
            {
                "name": "Website Tax Selection User",
                "login": "website_tax_selection_user",
                "email": "website-tax-selection-user@example.com",
                "partner_id": cls.contact_partner.id,
            }
        )

    def _get_website_for_user(self, user):
        return self.website.with_env(self.env(user=user))

    def test_00_empty_partner_field_uses_website_default(self):
        """Test empty partner tax display uses standard website behavior."""
        self.contact_partner.website_show_line_subtotals_tax_selection = False
        self.company_partner.website_show_line_subtotals_tax_selection = False
        website = self._get_website_for_user(self.website_user)

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_excluded",
            )

    def test_01_logged_user_partner_can_specify_tax_included(self):
        """Test logged-in partner can specify tax-included website prices."""
        self.company_partner.website_show_line_subtotals_tax_selection = "tax_included"
        website = self._get_website_for_user(self.website_user)

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_included",
            )

    def test_02_public_user_partner_can_specify_tax_included(self):
        """Test public user partner can specify tax-included website prices."""
        self.public_partner.website_show_line_subtotals_tax_selection = "tax_included"
        website = self._get_website_for_user(self.public_user)

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_included",
            )

    def test_03_commercial_partner_value_is_propagated_to_contact(self):
        """Test commercial partner tax display is propagated to contacts."""
        self.company_partner.website_show_line_subtotals_tax_selection = "tax_included"
        self.assertEqual(
            self.contact_partner.website_show_line_subtotals_tax_selection,
            "tax_included",
        )
        website = self._get_website_for_user(self.website_user)

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_included",
            )

    def test_04_commercial_partner_changes_sync_to_contact(self):
        """Test commercial partner tax display changes sync to contacts."""
        self.company_partner.website_show_line_subtotals_tax_selection = "tax_included"
        self.assertEqual(
            self.contact_partner.website_show_line_subtotals_tax_selection,
            "tax_included",
        )

        self.company_partner.website_show_line_subtotals_tax_selection = "tax_excluded"
        self.assertEqual(
            self.contact_partner.website_show_line_subtotals_tax_selection,
            "tax_excluded",
        )

        website = self._get_website_for_user(self.website_user)
        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_excluded",
            )

        self.company_partner.website_show_line_subtotals_tax_selection = "tax_included"

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_included",
            )

    def test_05_cleared_partner_value_returns_to_standard_behavior(self):
        """Test clearing partner tax display returns to standard website behavior."""
        self.company_partner.website_show_line_subtotals_tax_selection = "tax_included"
        website = self._get_website_for_user(self.website_user)

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_included",
            )

        self.company_partner.website_show_line_subtotals_tax_selection = False

        with MockRequest(website.env, website=website):
            self.assertEqual(
                website.show_line_subtotals_tax_selection,
                "tax_excluded",
            )

    def test_06_public_product_price_uses_tax_included_display(self):
        """Test public product display price uses tax-included partner selection."""
        self.public_partner.website_show_line_subtotals_tax_selection = "tax_included"
        tax = self.env["account.tax"].create({"name": "Test Tax 10%", "amount": 10})
        product = self._create_product(list_price=100, taxes_id=[Command.link(tax.id)])
        website = self._get_website_for_user(self.public_user)

        with MockRequest(website.env, website=website):
            configurator_price = website.env[
                "product.template"
            ]._get_configurator_display_price(
                product_or_template=product.with_env(website.env),
                quantity=1,
                date=datetime(2000, 1, 1),
                currency=self.currency,
                pricelist=self.pricelist,
            )

        self.assertEqual(configurator_price[0], 110)
