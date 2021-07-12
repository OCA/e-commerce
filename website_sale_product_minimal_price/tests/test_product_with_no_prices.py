# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class TestProductWithNoPrices(HttpCase):
    """ With this test we are checking that the minimal price is set
        when the product has not a price defined and the price of
        variants depend on a subpricelist.
    """

    def setUp(self):
        super().setUp()
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        self.category = self.env["product.category"].create({"name": "Test category"})
        self.product_attribute = ProductAttribute.create(
            {"name": "Test", "create_variant": "always"}
        )
        self.product_attribute_value_test_1 = ProductAttributeValue.create(
            {"name": "Test v1", "attribute_id": self.product_attribute.id}
        )
        self.product_attribute_value_test_2 = ProductAttributeValue.create(
            {"name": "Test v2", "attribute_id": self.product_attribute.id}
        )
        self.product_template = self.env["product.template"].create(
            {
                "name": "My product test with no prices",
                "is_published": True,
                "type": "consu",
                "website_sequence": 1,
                "categ_id": self.category.id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.product_attribute.id,
                            "value_ids": [
                                (4, self.product_attribute_value_test_1.id),
                                (4, self.product_attribute_value_test_2.id),
                            ],
                        },
                    ),
                ],
            }
        )
        self.variant_1 = self.product_template.product_variant_ids[0]
        self.variant_2 = self.product_template.product_variant_ids[1]
        self.pricelist_aux = self.env["product.pricelist"].create(
            {
                "name": "Test pricelist Aux",
                "selectable": True,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.variant_1.id,
                            "compute_price": "fixed",
                            "fixed_price": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.variant_2.id,
                            "compute_price": "fixed",
                            "fixed_price": 11,
                        },
                    ),
                ],
            }
        )
        self.pricelist_main = self.env["product.pricelist"].create(
            {
                "name": "Test pricelist Main",
                "selectable": True,
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "2_product_category",
                            "categ_id": self.category.id,
                            "compute_price": "formula",
                            "base": "pricelist",
                            "base_pricelist_id": self.pricelist_aux.id,
                        },
                    )
                ],
            }
        )
        user = self.env.ref("base.user_admin")
        user.property_product_pricelist = self.pricelist_main

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/", "test_product_with_no_prices", login="admin")
