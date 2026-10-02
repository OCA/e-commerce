# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.website.tools import MockRequest
from odoo.addons.website_sale_tax_toggle.controllers.main import WebsiteSaleTaxToggle


@tagged("post_install", "-at_install")
class WebsiteSaleTaxesToggleHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Get company for Mitchel Admin user
        cls.user_admin = cls.env.ref("base.user_admin")
        user_company = cls.user_admin.company_id
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
                "taxes_id": [(6, 0, cls.tax.ids)],
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

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            url_path="/shop",
            tour_name="website_sale_tax_toggle",
            login="admin",
        )

    def test_tax_toggle_route_initializes_session(self):
        """Without value in the session, the route starts from the website setting.

        ``_frontend_pre_dispatch`` already sets the value for HTTP requests, so
        the controller is called directly.
        """
        website = self.env["website"].get_current_website()
        for preactivated in (False, True):
            website.tax_toggle_preactivated = preactivated
            with MockRequest(self.env, website=website) as request:
                taxed = WebsiteSaleTaxToggle().tax_toggle()
                self.assertEqual(taxed, not preactivated)
                self.assertEqual(request.session["tax_toggle_taxed"], taxed)
