# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleProductMinimalPriceHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        # Create and select a pricelist
        # to make tests pass no matter what l10n package is enabled
        self.website = self.env["website"].get_current_website()
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "website_sale_product_minimal_price public",
                "currency_id": self.env.company.currency_id.id,
                "selectable": True,
                "sequence": 1,
                "website_id": self.website.id,
            }
        )
        self.env.ref("base.user_admin").property_product_pricelist = pricelist
        # Models
        ProductAttribute = self.env["product.attribute"]
        ProductAttributeValue = self.env["product.attribute.value"]
        ProductTmplAttributeValue = self.env["product.template.attribute.value"]
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
                "name": "My product test with various prices",
                "is_published": True,
                "type": "consu",
                "list_price": 100.0,
                "website_id": self.website.id,
                "website_sequence": 1,
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
        product_tmpl_att_value = ProductTmplAttributeValue.search(
            [
                ("product_tmpl_id", "=", self.product_template.id),
                ("attribute_id", "=", self.product_attribute.id),
                (
                    "product_attribute_value_id",
                    "=",
                    self.product_attribute_value_test_1.id,
                ),
            ]
        )
        product_tmpl_att_value.price_extra = 50.0
        product_tmpl_att_value = ProductTmplAttributeValue.search(
            [
                ("product_tmpl_id", "=", self.product_template.id),
                ("attribute_id", "=", self.product_attribute.id),
                (
                    "product_attribute_value_id",
                    "=",
                    self.product_attribute_value_test_2.id,
                ),
            ]
        )
        product_tmpl_att_value.price_extra = 25.0

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour("/shop", "website_sale_product_minimal_price", login="admin")
