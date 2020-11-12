# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged, common


@tagged('post_install', '-at_install')
class WebsiteSaleHttpCase(common.HttpCase):

    def setUp(self):
        super().setUp()
        self.partner_company = self.env["res.partner"].create({
            "name": "Mr. Odoo's company",
        })
        self.partner = self.env.ref("base.partner_demo_portal")
        self.partner.parent_id = self.partner_company
        self.partner_invoice = self.env["res.partner"].create({
            "name": "Mr. Odoo's accountant",
            "type": "invoice",
            "parent_id": self.partner_company.id,
        })

    def test_website_sale_invoice_partner(self):
        """Make an order from the frontend and check that the invoice address
        is the right one"""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_invoice_address_tour",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours.%s.ready" % tour,
            login="portal",
        )
        order = self.env["sale.order"].search([
            ("partner_id", "=", self.partner.id)
        ], limit=1)
        self.assertEqual(order.partner_invoice_id, self.partner_invoice)
