# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleSecondaryUnitHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        # Models
        ProductSecondaryUnit = self.env["product.secondary.unit"]
        product_uom_unit = self.env.ref("uom.product_uom_unit")
        self.product_template = self.env["product.template"].create(
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
            "product_tmpl_id": self.product_template.id,
            "website_published": True,
        }
        self.secondary_unit_box_5 = ProductSecondaryUnit.create(vals)
        self.secondary_unit_box_10 = ProductSecondaryUnit.create(
            dict(vals, factor=10.0)
        )
        self.product_template.write(
            {
                "secondary_uom_ids": [
                    (
                        6,
                        0,
                        [self.secondary_unit_box_5.id, self.secondary_unit_box_10.id],
                    ),
                ],
            }
        )
        # Add group "Manage Multiple Units of Measure" to admin
        admin = self.env.ref("base.user_admin")
        admin.groups_id |= self.browse_ref("uom.group_uom")

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_secondary_unit", login="admin")
