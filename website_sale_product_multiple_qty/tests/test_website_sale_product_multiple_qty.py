# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.fields import Command
from odoo.tests import tagged
from odoo.tools.misc import file_open

from odoo.addons.base.tests.common import HttpCaseWithUserDemo


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductMultipleQTY(HttpCaseWithUserDemo):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ProductAttribute = cls.env["product.attribute"]
        cls.ProductAttributeValue = cls.env["product.attribute.value"]
        cls.UoM = cls.env["uom.uom"]
        cls.base_uom = cls.env.ref("uom.product_uom_unit")
        settings_vals = {
            "group_product_variant": True,
            "group_uom": True,
            "group_show_uom_price": True,
        }
        cls.env["res.config.settings"].create(settings_vals).execute()
        # Setup multiple UoMs
        cls.box_of_5 = cls.UoM.create(
            {
                "name": "Box of 5",
                "relative_factor": 5,
                "relative_uom_id": cls.base_uom.id,
            }
        )
        cls.box_of_13 = cls.UoM.create(
            {
                "name": "Box of 13",
                "relative_factor": 13,
                "relative_uom_id": cls.base_uom.id,
            }
        )
        # Setup attributes and attributes values
        cls.product_attribute_1 = cls.ProductAttribute.create(
            {
                "name": "Color",
                "display_type": "color",
                "sequence": 20,
            }
        )
        cls.product_attribute_2 = cls.ProductAttribute.create(
            {
                "name": "Legs",
                "sequence": 10,
            }
        )
        cls.product_attribute_value_1 = cls.ProductAttributeValue.create(
            {
                "name": "White",
                "attribute_id": cls.product_attribute_1.id,
                "html_color": "#FFFFFF",
                "sequence": 1,
            }
        )
        cls.product_attribute_value_2 = cls.ProductAttributeValue.create(
            {
                "name": "Black",
                "attribute_id": cls.product_attribute_1.id,
                "html_color": "#000000",
                "sequence": 2,
            }
        )
        cls.product_attribute_value_3 = cls.ProductAttributeValue.create(
            {
                "name": "Steel",
                "attribute_id": cls.product_attribute_2.id,
                "sequence": 1,
            }
        )
        cls.product_attribute_value_4 = cls.ProductAttributeValue.create(
            {
                "name": "Aluminium",
                "attribute_id": cls.product_attribute_2.id,
                "sequence": 2,
            }
        )
        # Create product template
        cls.product_product_custo_desk = cls.ProductTemplate.create(
            {
                "name": "website_sale_cart_product_desk",
                "standard_price": 500.0,
                "list_price": 750.0,
                "sale_multiple_uom_id": cls.box_of_5.id,
                "website_published": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.product_attribute_1.id,
                            "value_ids": [
                                Command.link(cls.product_attribute_value_1.id),
                                Command.link(cls.product_attribute_value_2.id),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.product_attribute_2.id,
                            "value_ids": [
                                Command.link(cls.product_attribute_value_3.id),
                                Command.link(cls.product_attribute_value_4.id),
                            ],
                        }
                    ),
                ],
            }
        )

        # Setup an optional product
        img_path = "product/static/img/product_product_11-image.jpg"
        img_content = base64.b64encode(file_open(img_path, "rb").read())
        cls.product_product_conf_chair = cls.ProductTemplate.create(
            {
                "name": "website_sale_cart_product_chair",
                "image_1920": img_content,
                "list_price": 16.50,
                "sale_multiple_uom_id": cls.box_of_13.id,
                "website_published": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.product_attribute_2.id,
                            "value_ids": [
                                Command.link(cls.product_attribute_value_3.id),
                                Command.link(cls.product_attribute_value_4.id),
                            ],
                        }
                    )
                ],
            }
        )
        cls.product_product_custo_desk.optional_product_ids = [
            Command.link(cls.product_product_conf_chair.id)
        ]
        # Setup product variants with different sales multiple UoM
        # We sell:
        #   the white desk by box of 5 and the black desk by unit.
        #   the white chair by box of 13 and the black chair by unit.
        desk_variants = cls.product_product_custo_desk.product_variant_ids
        chair_variants = cls.product_product_conf_chair.product_variant_ids
        cls.variant_custo_desk_steel_white = desk_variants[0]
        cls.variant_conf_chair_white = chair_variants[0]
        cls.variant_custo_desk_steel_white.write(
            {
                "name": "website_sale_cart_product_desk_steel_white",
                "sale_multiple_uom_id": cls.box_of_5.id,
            }
        )
        cls.variant_conf_chair_white.write(
            {
                "name": "website_sale_cart_product_chair_white",
                "sale_multiple_uom_id": cls.box_of_13.id,
            }
        )

    def test_00_demo_tour_shop_product_multiple_qty(self):
        """Check multiple qty for shop product cart and configurator.

        Using "demo" user in the tests.
        """
        self.start_tour("/", "tour_shop_product_multiple_qty", login="demo")

    def test_01_demo_tour_shop_checkout_product_multiple_qty(self):
        """Check multiple qty for shop product checkout.

        Using "admin" user in the tests for the checkout tour.
        """
        self.start_tour("/", "tour_shop_checkout_product_multiple_qty", login="admin")
