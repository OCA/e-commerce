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
        # Add group "Manage Multiple Units of Measure" to admin
        admin = cls.env.ref("base.user_admin")
        admin.groups_id |= cls.env.ref("uom.group_uom")
        # Force VAT to avoid error in the module that makes it required.
        admin.partner_id.vat = "TEST12345678"

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop", "website_sale_secondary_unit", login="admin", step_delay=1000
        )
