# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)
# Copyright 2026 Tecnativa - Pilar Vargas

from odoo import Command
from odoo.tests import HttpCase, tagged

from odoo.addons.http_routing.models.ir_http import slug


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductMatrixHidePrice(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attr_color = cls.env["product.attribute"].create({"name": "Color"})
        cls.attr_size = cls.env["product.attribute"].create({"name": "Size"})
        cls.color_red = cls.env["product.attribute.value"].create(
            {
                "name": "Red",
                "attribute_id": cls.attr_color.id,
            }
        )
        cls.color_blue = cls.env["product.attribute.value"].create(
            {
                "name": "Blue",
                "attribute_id": cls.attr_color.id,
            }
        )
        cls.size_s = cls.env["product.attribute.value"].create(
            {
                "name": "S",
                "attribute_id": cls.attr_size.id,
            }
        )
        cls.size_m = cls.env["product.attribute.value"].create(
            {
                "name": "M",
                "attribute_id": cls.attr_size.id,
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Matrix Product",
                "sale_ok": True,
                "is_published": True,
                "list_price": 10.0,
                "product_add_mode": "matrix",
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attr_color.id,
                            "value_ids": [
                                Command.set(
                                    [
                                        cls.color_red.id,
                                        cls.color_blue.id,
                                    ]
                                ),
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.attr_size.id,
                            "value_ids": [
                                Command.set(
                                    [
                                        cls.size_s.id,
                                        cls.size_m.id,
                                    ]
                                ),
                            ],
                        }
                    ),
                ],
            }
        )

    def _get_product_page(self):
        response = self.url_open(f"/shop/product/{slug(self.product)}")
        return response.text

    def test_matrix_add_to_cart_button_is_shown_when_price_is_visible(self):
        self.product.website_hide_price = False
        html = self._get_product_page()
        self.assertIn('href="#modalMatrix"', html)

    def test_matrix_add_to_cart_button_is_hidden_when_price_is_hidden(self):
        self.product.website_hide_price = True
        html = self._get_product_page()
        self.assertNotIn('href="#modalMatrix"', html)
