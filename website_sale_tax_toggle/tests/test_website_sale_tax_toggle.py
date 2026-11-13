# Copyright 2020 Tecnativa - Sergio Teruel
# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CREATE_CONTEXT
from odoo.addons.website_sale.tests.common import MockRequest


@tagged("post_install", "-at_install")
class WebsiteSaleTaxesToggleHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_website_sale_tax_toggle=True,
                **DISABLED_MAIL_CREATE_CONTEXT,
            )
        )
        # Get company for Mitchel Admin user
        cls.user_admin = cls.env.ref("base.user_admin")
        user_company = cls.user_admin.company_id
        cls.website = user_company.website_id
        if not cls.website:
            cls.website = cls.env["website"].create(
                {"name": "Tax toggle test website", "company_id": user_company.id}
            )
        cls.website.show_line_subtotals_tax_selection = "tax_excluded"
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Taxes toggle test tax",
                "amount_type": "percent",
                "amount": 15,
                "type_tax_use": "sale",
                "company_id": user_company.id,
            }
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Product test tax toggle",
                "list_price": 750.00,
                "taxes_id": [Command.set(cls.tax.ids)],
                "website_published": True,
                "website_sequence": 9999,
            }
        )
        pricelist = cls.env["product.pricelist"].create(
            {"name": "Price list for tests", "currency_id": user_company.currency_id.id}
        )
        cls.env.user.partner_id.property_product_pricelist = pricelist
        # To avoid currency converter
        cls.env["res.currency.rate"].search([]).write({"rate": 1})

    def test_apply_taxes_from_session(self):
        """Resolve omitted taxes for both templates and product variants."""
        for product in (
            self.product_template,
            self.product_template.product_variant_id,
        ):
            for show_tax, expected in ((False, 750.0), (True, 862.5)):
                with self.subTest(model=product._name, show_tax=show_tax):
                    with MockRequest(self.env, website=self.website) as request:
                        request.session["tax_toggle_taxed"] = show_tax
                        request.fiscal_position = self.env["account.fiscal.position"]
                        price = product._apply_taxes_to_price(
                            750.0,
                            self.website.currency_id,
                            website=self.website,
                        )
                    self.assertAlmostEqual(price, expected, places=2)

    def test_apply_taxes_with_fiscal_position(self):
        """Use the mapped tax instead of the original product tax."""
        fiscal_position = self.env["account.fiscal.position"].create(
            {"name": "Tax toggle fiscal position"}
        )
        self.tax.copy(
            {
                "name": "Mapped tax",
                "amount": 5,
                "fiscal_position_ids": [Command.set(fiscal_position.ids)],
                "original_tax_ids": [Command.set(self.tax.ids)],
            }
        )
        for show_tax, expected in ((False, 750.0), (True, 787.5)):
            with self.subTest(show_tax=show_tax):
                with MockRequest(self.env, website=self.website) as request:
                    request.session["tax_toggle_taxed"] = show_tax
                    request.fiscal_position = fiscal_position
                    price = self.product_template._apply_taxes_to_price(
                        750.0,
                        self.website.currency_id,
                        website=self.website,
                    )
                self.assertAlmostEqual(price, expected, places=2)

    def test_apply_taxes_without_product_taxes(self):
        self.product_template.taxes_id = False
        with MockRequest(self.env, website=self.website) as request:
            request.session["tax_toggle_taxed"] = True
            price = self.product_template._apply_taxes_to_price(
                750.0,
                self.website.currency_id,
                website=self.website,
            )
        self.assertEqual(price, 750.0)

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            url_path="/shop?search=Product+test+tax+toggle",
            tour_name="website_sale_tax_toggle",
            login="admin",
        )
