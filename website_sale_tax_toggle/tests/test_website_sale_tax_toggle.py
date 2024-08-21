# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged
from odoo.tests.common import HttpCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


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
