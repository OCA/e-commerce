# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
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
        website = self.env["website"].with_user(portal_user).search([], limit=1)
        templates = self.partner.with_user(portal_user)._get_my_regular_products(
            website
        )
        self.assertIn(self.products["Alpha Product"].product_tmpl_id, templates)
        self.assertNotIn(self.products["Echo Product"].product_tmpl_id, templates)

        # The portal card badge counts products a customer can buy again:
        # unpublished products are excluded even for internal users.
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card", "True"
        )
        response = self.url_open(
            "/my/counters",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "id": 1,
                    "params": {"counters": ["my_regular_products_count"]},
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        expected = len(
            self.partner._get_my_regular_products(website).filtered("is_published")
        )
        self.assertEqual(
            response.json()["result"]["my_regular_products_count"], expected
        )
        # Echo Product is bought but not published: it must not be counted.
        # Browse the website as an internal user so unpublished products are
        # included in the total, like they are for the shop itself.
        admin_website = self.env["website"].search([], limit=1)
        self.assertLess(
            response.json()["result"]["my_regular_products_count"],
            len(self.partner._get_my_regular_products(admin_website)),
        )

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

    def test_menu_label_is_configurable(self):
        """As a shop manager, I can change the label of the link to my
        regular products in the shop."""
        # The label is a translated field: set it in every installed
        # language so the page renders it whatever the website language is.
        for code, _name in self.env["res.lang"].get_installed():
            self.env.company.with_context(
                lang=code
            ).regular_products_menu_label = "Bought Before"

        self.authenticate("admin", "admin")
        response = self.url_open("/shop")
        self.assertIn("Bought Before", response.text)

    def test_portal_card_is_hidden_by_default(self):
        """As a customer, I don't see a card for my regular products on my
        portal home page until the shop manager enables it."""
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card", "False"
        )
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal User",
                "login": "portal_user",
                "password": "portal_user",
                "group_ids": [Command.set(portal_group.ids)],
            }
        )
        self.authenticate(portal_user.login, "portal_user")
        response = self.url_open("/my")
        self.assertNotIn("/shop/my_regular_products", response.text)

        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card", "True"
        )
        response = self.url_open("/my")
        self.assertIn("/shop/my_regular_products", response.text)
        self.assertIn("Products you bought before, to buy again", response.text)

        # The card description is configurable per company.
        self.env.company.regular_products_card_text = "Buy them again"
        response = self.url_open("/my")
        self.assertIn("Buy them again", response.text)

    def test_portal_card_position_is_configurable(self):
        """As a shop manager, I can choose where the 'My Regular Products'
        card is displayed on the customer portal home page."""
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card", "True"
        )
        portal_group = self.env.ref("base.group_portal")
        portal_user = self.env["res.users"].create(
            {
                "name": "Portal User",
                "login": "portal_user",
                "password": "portal_user",
                "group_ids": [Command.set(portal_group.ids)],
            }
        )
        self.authenticate(portal_user.login, "portal_user")

        def card_snippet(html):
            index = html.index('href="/shop/my_regular_products"')
            start = html.rfind("o_portal_index_card", 0, index)
            return html[start:index]

        # Top banner (default): a full-width card in the top section.
        html = self.url_open("/my").text
        self.assertIn("col-12", card_snippet(html))
        self.assertLess(
            html.index("/shop/my_regular_products"), html.index("/my/orders")
        )

        # Inline: a half-width card right before the Orders card.
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card_position",
            "inline",
        )
        html = self.url_open("/my").text
        self.assertIn("col-md-6", card_snippet(html))
        self.assertLess(
            html.index("/shop/my_regular_products"), html.index("/my/orders")
        )

        # Bottom banner: a full-width card after the common category.
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.portal_card_position",
            "bottom",
        )
        html = self.url_open("/my").text
        self.assertIn("col-12", card_snippet(html))
        self.assertGreater(
            html.index("/shop/my_regular_products"),
            html.index('id="portal_common_category"'),
        )
