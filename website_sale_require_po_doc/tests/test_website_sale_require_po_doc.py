# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@odoo.tests.tagged("post_install", "-at_install")
class TestWebsiteSaleRequirePoDoc(odoo.tests.HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.partner = cls.env.ref("base.partner_admin")
        cls.env["product.template"].create(
            {
                "name": "Test Product",
                "list_price": 0.0,
                "sale_ok": True,
                "is_published": True,
            }
        )
        cls.env["res.users"].search([("login", "=", "admin")]).partner_id.write(
            {
                "country_id": cls.env.ref("base.us").id,
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345",
                "email": "admin@example.com",
                "phone": "1234567890",
                "state_id": cls.env.ref("base.state_us_1").id,
            }
        )

    def _get_last_order(self, state=None):
        domain = [("partner_id", "=", self.partner.id)]
        if state:
            domain.append(("state", "=", state))
        return self.env["sale.order"].search(domain, order="id desc", limit=1)

    def test_ui_po_required_with_value(self):
        """PO field is shown and client_order_ref is saved on the order."""
        self.partner.customer_need_po = True
        self.start_tour(
            "/",
            "website_sale_require_po_doc_with_value",
            login="admin",
        )
        self.assertEqual(self._get_last_order().client_order_ref, "PO-12345")

    def test_ui_po_required_without_value(self):
        """PO field blocks submission when left empty."""
        self.partner.customer_need_po = True
        self.start_tour(
            "/",
            "website_sale_require_po_doc_without_value",
            login="admin",
        )

    def test_ui_po_not_required(self):
        """PO field is not shown and client_order_ref remains empty."""
        self.partner.customer_need_po = False
        self.start_tour(
            "/",
            "website_sale_require_po_doc_not_required",
            login="admin",
        )
        self.assertFalse(self._get_last_order(state="draft").client_order_ref)
