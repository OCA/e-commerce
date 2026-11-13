# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import Command, fields
from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestMyRegularProducts(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Display the categories menu, where the link to the page is shown.
        cls.env.ref("website_sale.products_categories").active = True
        cls.partner = cls.env.ref("base.user_admin").partner_id
        cls.other_partner = cls.env["res.partner"].create({"name": "Other Customer"})
        cls.products = {}
        for name in (
            "Bravo Product",
            "Alpha Product",
            "Charlie Product",
            "Delta Product",
            "Echo Product",
        ):
            product = cls.env["product.product"].create(
                {"name": name, "list_price": 10.0}
            )
            product.product_tmpl_id.website_published = True
            cls.products[name] = product
        # Bought by the customer but not published on the shop.
        cls.products["Echo Product"].product_tmpl_id.website_published = False

    def _confirm_order(self, partner, lines, confirm=True, date_order=None):
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "price_unit": product.list_price,
                        }
                    )
                    for product, qty in lines
                ],
            }
        )
        if confirm:
            order.action_confirm()
        if date_order:
            # action_confirm resets date_order to now.
            order.date_order = date_order
        return order

    def _get_regular_products_page(self):
        self.authenticate("admin", "admin")
        return self.url_open("/shop/my_regular_products")

    def test_page_lists_products_most_bought_first(self):
        """As a customer, I see the products I bought most on my regular
        products page, and not the products bought by others or still in
        quotation. Unpublished products are hidden from non-internal
        users."""
        self._confirm_order(
            self.partner,
            [
                (self.products["Bravo Product"], 30),
                (self.products["Alpha Product"], 50),
            ],
        )
        # Draft quotation: not counted.
        self._confirm_order(
            self.partner, [(self.products["Delta Product"], 100)], confirm=False
        )
        # Another customer: not counted.
        self._confirm_order(
            self.other_partner, [(self.products["Charlie Product"], 70)]
        )
        # Not published on the shop: not shown.
        self._confirm_order(self.partner, [(self.products["Echo Product"], 200)])

        response = self._get_regular_products_page()
        self.assertEqual(response.status_code, 200)
        html = response.text
        self.assertIn("Alpha Product", html)
        self.assertIn("Bravo Product", html)
        self.assertLess(html.index("Alpha Product"), html.index("Bravo Product"))
        for name in ("Charlie Product", "Delta Product"):
            self.assertNotIn(name, html)
        # Internal users can preview unpublished products, like on the
        # shop itself; check the published filter as a portal user.
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal User",
                "login": "portal_user",
                "group_ids": [Command.link(self.env.ref("base.group_portal").id)],
            }
        )
        website = self.env["website"].search([], limit=1)
        templates = self.partner.with_user(portal_user)._get_my_regular_products(
            website
        )
        self.assertIn(self.products["Alpha Product"].product_tmpl_id, templates)
        self.assertNotIn(self.products["Echo Product"].product_tmpl_id, templates)

    def test_page_is_limited_to_configured_number_of_products(self):
        """As a shop manager, I can limit how many regular products are
        displayed on the page."""
        self._confirm_order(
            self.partner,
            [
                (self.products["Alpha Product"], 50),
                (self.products["Bravo Product"], 30),
                (self.products["Charlie Product"], 10),
            ],
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.limit", "2"
        )

        response = self._get_regular_products_page()
        html = response.text
        self.assertIn("Alpha Product", html)
        self.assertIn("Bravo Product", html)
        self.assertNotIn("Charlie Product", html)

    def test_orders_older_than_configured_period_are_not_counted(self):
        """As a shop manager, I can limit how far back orders are counted
        on my regular products page."""
        old_date = fields.Datetime.now() - timedelta(days=60)
        self._confirm_order(
            self.partner,
            [(self.products["Alpha Product"], 100)],
            date_order=old_date,
        )
        self._confirm_order(self.partner, [(self.products["Bravo Product"], 10)])
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.period_days", "30"
        )

        response = self._get_regular_products_page()
        html = response.text
        self.assertNotIn("Alpha Product", html)
        self.assertIn("Bravo Product", html)
