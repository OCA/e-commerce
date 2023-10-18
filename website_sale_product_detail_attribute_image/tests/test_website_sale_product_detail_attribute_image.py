# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):
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
        cls.ProductAttribute = cls.env["product.attribute"]
        cls.ProductAttributeValue = cls.env["product.attribute.value"]
        cls.ProductAttributeLine = cls.env["product.template.attribute.line"]

        detail_image = "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="

        attribute_dangerous = cls.ProductAttribute.create(
            {
                "name": "Dangerousness",
                "create_variant": "no_variant",
                "website_product_detail_image_published": False,
                "website_product_detail_image": detail_image,
            }
        )
        product_attribute_image_high = cls.ProductAttributeValue.create(
            {"name": "High dangerousness", "attribute_id": attribute_dangerous.id}
        )
        cls.ProductAttributeValue.create(
            {"name": "Low dangerousness", "attribute_id": attribute_dangerous.id}
        )
        cls.product_template = cls.env.ref("product.product_product_4_product_template")
        attribute_line = cls.ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template.id,
                "attribute_id": attribute_dangerous.id,
                "value_ids": [(6, 0, product_attribute_image_high.ids)],
            }
        )
        cls.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})
        attribute_image_policy_one = cls.ProductAttribute.create(
            {
                "name": "Policy One",
                "website_name": "Website Policy One",
                "create_variant": "no_variant",
                "website_product_detail_image_published": True,
                "website_product_detail_image": detail_image,
            }
        )
        value_image_policy_one_1 = cls.ProductAttributeValue.create(
            {
                "name": "Policy One Value 1",
                "website_name": "Policy One Value 1 for website",
                "attribute_id": attribute_image_policy_one.id,
            }
        )
        attribute_line = cls.ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template.id,
                "attribute_id": attribute_image_policy_one.id,
                "value_ids": [(6, 0, value_image_policy_one_1.ids)],
            }
        )
        cls.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})

        attribute_image_policy_two = cls.ProductAttribute.create(
            {
                "name": "Policy Two",
                "create_variant": "no_variant",
                "website_product_detail_image_published": True,
                "website_product_detail_image": detail_image,
            }
        )
        value_image_policy_two_1 = cls.ProductAttributeValue.create(
            {
                "name": "Policy Two Value 1",
                "attribute_id": attribute_image_policy_two.id,
            }
        )
        attribute_line = cls.ProductAttributeLine.create(
            {
                "product_tmpl_id": cls.product_template.id,
                "attribute_id": attribute_image_policy_two.id,
                "value_ids": [(6, 0, value_image_policy_two_1.ids)],
            }
        )
        cls.product_template.write({"attribute_line_ids": [(4, attribute_line.id)]})

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
