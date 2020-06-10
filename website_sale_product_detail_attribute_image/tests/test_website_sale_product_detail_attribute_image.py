# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        self.ProductAttribute = self.env["product.attribute"]
        self.ProductAttributeValue = self.env["product.attribute.value"]
        self.ProductAttributeLine = self.env["product.template.attribute.line"]

        detail_image = "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="

        attribute_dangerous = self.ProductAttribute.create(
            {
                "name": "Dangerousness",
                "create_variant": "no_variant",
                "website_product_detail_image_published": False,
                "website_product_detail_image": detail_image,
            }
        )
        product_attribute_image_high = self.ProductAttributeValue.create(
            {"name": "High dangerousness", "attribute_id": attribute_dangerous.id}
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
            {
                "name": "Policy One",
                "website_name": "Website Policy One",
                "create_variant": "no_variant",
                "website_product_detail_image_published": True,
                "website_product_detail_image": detail_image,
            }
        )
        value_image_policy_one_1 = self.ProductAttributeValue.create(
            {
                "name": "Policy One Value 1",
                "website_name": "Policy One Value 1 for website",
                "attribute_id": attribute_image_policy_one.id,
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
            {
                "name": "Policy Two",
                "create_variant": "no_variant",
                "website_product_detail_image_published": True,
                "website_product_detail_image": detail_image,
            }
        )
        value_image_policy_two_1 = self.ProductAttributeValue.create(
            {
                "name": "Policy Two Value 1",
                "attribute_id": attribute_image_policy_two.id,
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
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_product_detail_attribute_image",
        )
        self.browser_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )
