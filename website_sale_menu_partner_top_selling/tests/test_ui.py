# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestUi(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env.ref("website_sale.products_categories").active = True
        cls.env["ir.config_parameter"].sudo().set_param(
            "website_sale_menu_partner_top_selling.limit", 2
        )
        cls.admin_user = cls.env.ref("base.user_admin")
        cls.partner = cls.admin_user.partner_id
        cls.products = []
        for i in range(1, 6):
            product = cls.env["product.product"].create(
                {
                    "name": f"Product {i}",
                    "list_price": 10.0 * i,
                }
            )
            product.product_tmpl_id.website_published = True
            cls.products.append(product)
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        quantities = [50, 30, 70, 10, 90]
        for product, qty in zip(cls.products, quantities):
            cls.env["sale.order.line"].create(
                {
                    "order_id": cls.sale_order.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "price_unit": product.list_price,
                }
            )
        cls.sale_order.action_confirm()
        # Unconfirmed order, no products to be counted
        cls.sale_order_2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.env["sale.order.line"].create(
            {
                "order_id": cls.sale_order_2.id,
                "product_id": cls.products[0].id,
                "product_uom_qty": 1000,
                "price_unit": cls.products[0].list_price,
            }
        )

    def test_ui(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_menu_partner_top_selling",
            login="admin",
        )
