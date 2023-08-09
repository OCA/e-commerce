# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import new_test_user, tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class WebsiteSaleProductAttributeFilterCollapseHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        self.product_attribute = self.env["product.attribute"].create(
            {
                "name": "Test a1",
            }
        )
        self.product_attribute_value_1 = self.env["product.attribute.value"].create(
            {"name": "Test v1", "attribute_id": self.product_attribute.id}
        )
        self.product_attribute_value_2 = self.env["product.attribute.value"].create(
            {"name": "Test v2", "attribute_id": self.product_attribute.id}
        )
        self.product_template = self.env.ref(
            "product.product_product_4_product_template"
        )
        self.product_attribute_line = self.env[
            "product.template.attribute.line"
        ].create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.product_attribute_value_1.id,
                            self.product_attribute_value_2.id,
                        ],
                    )
                ],
            }
        )
        self.product_template.write(
            {
                "attribute_line_ids": [(4, self.product_attribute_line.id)],
                "is_published": True,
            }
        )
        # Active filter in /shop.
        self.env.ref(
            "website_sale_product_attribute_filter_collapse.products_attributes_collapsible"
        ).active = True
        # Create new user
        new_test_user(self.env, login="portal_user", groups="base.group_portal")

    def test_tour(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop",
            "website_sale_product_attribute_filter_collapse",
            login="portal_user",
        )
