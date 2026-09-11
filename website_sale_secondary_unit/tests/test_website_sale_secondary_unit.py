# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests.common import HttpCase, tagged

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


@tagged("post_install", "-at_install")
class WebsiteSaleSecondaryUnitHttpCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # Models
        ProductSecondaryUnit = cls.env["product.secondary.unit"]
        product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test product",
                "is_published": True,
                "website_sequence": 1,
                "type": "consu",
                "uom_id": product_uom_unit.id,
            }
        )
        vals = {
            "name": "Box",
            "uom_id": product_uom_unit.id,
            "factor": 5.0,
            "product_tmpl_id": cls.product_template.id,
            "website_published": True,
        }
        cls.secondary_unit_box_5 = ProductSecondaryUnit.create(vals)
        cls.secondary_unit_box_10 = ProductSecondaryUnit.create(dict(vals, factor=10.0))
        cls.product_template.write(
            {
                "secondary_uom_ids": [
                    Command.set(
                        [cls.secondary_unit_box_5.id, cls.secondary_unit_box_10.id],
                    ),
                ],
            }
        )
        # A product with optional products opens the configurator dialog when
        # it is added to the cart, so it gets its own secondary units.
        cls.optional_product_template = cls.env["product.template"].create(
            {
                "name": "Test optional product",
                "is_published": True,
                "type": "consu",
                "uom_id": product_uom_unit.id,
            }
        )
        cls.configurable_product_template = cls.env["product.template"].create(
            {
                "name": "Test configurable product",
                "is_published": True,
                "website_sequence": 2,
                "type": "consu",
                "uom_id": product_uom_unit.id,
                "optional_product_ids": [
                    Command.set(cls.optional_product_template.ids)
                ],
            }
        )
        configurable_vals = dict(
            vals,
            factor=3.0,
            name="Pack",
            product_tmpl_id=cls.configurable_product_template.id,
        )
        ProductSecondaryUnit.create(configurable_vals)
        ProductSecondaryUnit.create(dict(configurable_vals, name="Box", factor=4.0))
        # Add group "Manage Multiple Units of Measure" to admin
        admin = cls.env.ref("base.user_admin")
        admin.group_ids |= cls.env.ref("uom.group_uom")
        # Force a valid VAT to avoid errors in the modules that make it required.
        admin.partner_id.vat = "BE0428759497"

    def test_reorder_from_portal_keeps_secondary_unit(self):
        """Reordering an order keeps the secondary unit and quantity of its lines."""
        # A product that can only be sold in secondary units is the worst case,
        # as the reordered quantity was converted twice.
        self.product_template.allow_uom_sell = False
        product = self.product_template.product_variant_id
        order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.user_admin").partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "secondary_uom_id": self.secondary_unit_box_5.id,
                            "product_uom_qty": 10.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product.id,
                            "secondary_uom_id": self.secondary_unit_box_10.id,
                            "product_uom_qty": 30.0,
                        }
                    ),
                ],
            }
        )
        order.action_confirm()
        self.assertEqual(order.order_line.mapped("secondary_uom_qty"), [2.0, 3.0])
        self.authenticate("admin", "admin")
        self.make_jsonrpc_request("/my/orders/reorder", {"order_id": order.id})
        cart = self.env["sale.order"].search(
            [("website_id", "!=", False), ("id", "!=", order.id)], limit=1
        )
        self.assertEqual(len(cart.order_line), 2)
        for line, original_line in zip(
            cart.order_line.sorted("id"), order.order_line, strict=True
        ):
            self.assertEqual(line.secondary_uom_id, original_line.secondary_uom_id)
            self.assertEqual(line.secondary_uom_qty, original_line.secondary_uom_qty)
            self.assertEqual(line.product_uom_qty, original_line.product_uom_qty)

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_secondary_unit", login="admin")

    def test_ui_website_configurator(self):
        """Test the secondary unit selector of the product configurator."""
        self.start_tour(
            "/shop",
            "website_sale_secondary_unit_configurator",
            login="admin",
        )
