# Copyright 2020 Tecnativa - Alexandre D. Díaz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo.tests


@odoo.tests.tagged("post_install", "-at_install")
class WebsiteSaleHttpCase(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        self.ProductAttribute = self.env["product.attribute"]
        self.ProductAttributeValue = self.env["product.attribute.value"]
        self.ProductAttributeLine = self.env["product.template.attribute.line"]

        attribute_dangerous = self.ProductAttribute.create(
            {"name": "Dangerousness", "create_variant": "no_variant"}
        )
        product_attribute_image_high = self.ProductAttributeValue.create(
            {
                "name": "High dangerousness",
                "attribute_id": attribute_dangerous.id,
                "website_product_detail_image_published": False,
                "website_product_detail_image": (
                    "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
                ),
            }
        )
        self.ProductAttributeValue.create(
            {"name": "Low dangerousness", "attribute_id": attribute_dangerous.id}
        )
        self.product_template = self.env.ref(
            "product.product_product_4_product_template"
        )
        attribute_line = self.ProductAttributeLine.create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": attribute_dangerous.id,
                "value_ids": [(6, 0, product_attribute_image_high.ids)],
            }
        )
        self.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})
        attribute_image_policy_one = self.ProductAttribute.create(
            {"name": "Policy One", "create_variant": "no_variant"}
        )
        value_image_policy_one_1 = self.ProductAttributeValue.create(
            {
                "name": "Policy One Value 1",
                "website_name": "Policy One Value 1 for website",
                "attribute_id": attribute_image_policy_one.id,
                "website_product_detail_image_published": True,
                "website_product_detail_image": (
                    "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
                ),
            }
        )
        attribute_line = self.ProductAttributeLine.create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": attribute_image_policy_one.id,
                "value_ids": [(6, 0, value_image_policy_one_1.ids)],
            }
        )
        self.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})

        attribute_image_policy_two = self.ProductAttribute.create(
            {"name": "Policy Two", "create_variant": "no_variant"}
        )
        value_image_policy_two_1 = self.ProductAttributeValue.create(
            {
                "name": "Policy Two Value 1",
                "attribute_id": attribute_image_policy_two.id,
                "website_product_detail_image_published": True,
                "website_product_detail_image": (
                    "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
                ),
            }
        )
        attribute_line = self.ProductAttributeLine.create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": attribute_image_policy_two.id,
                "value_ids": [(6, 0, value_image_policy_two_1.ids)],
            }
        )
        self.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})

    def test_ui_website(self):
        """Test frontend tour."""
        self.start_tour(
            "/shop", "website_sale_product_detail_attribute_value_image", login="admin"
        )
