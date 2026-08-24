# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleHideNoVariantAttributesTour(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Size",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Small"}),
                    Command.create({"name": "Large"}),
                ],
            }
        )
        cls.informational_attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Material",
                "create_variant": "no_variant",
                "value_ids": [
                    Command.create({"name": "Cotton"}),
                    Command.create({"name": "Wool"}),
                ],
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test product with mixed attributes",
                "sale_ok": True,
                "is_published": True,
                "list_price": 100.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.variant_attribute.id,
                            "value_ids": [
                                Command.set(cls.variant_attribute.value_ids.ids)
                            ],
                        }
                    ),
                    Command.create(
                        {
                            "attribute_id": cls.informational_attribute.id,
                            "value_ids": [
                                Command.set(cls.informational_attribute.value_ids.ids)
                            ],
                        }
                    ),
                ],
            }
        )
        variant_ptav_large = cls.product.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.variant_attribute
        ).product_template_value_ids.filtered(lambda ptav: ptav.name == "Large")
        informational_ptav_wool = cls.product.attribute_line_ids.filtered(
            lambda line: line.attribute_id == cls.informational_attribute
        ).product_template_value_ids.filtered(lambda ptav: ptav.name == "Wool")
        informational_ptav_wool.exclude_for = [
            Command.create(
                {
                    "product_tmpl_id": cls.product.id,
                    "value_ids": [Command.link(variant_ptav_large.id)],
                }
            )
        ]

    def test_hide_no_variant_attributes(self):
        self.start_tour(
            self.product.website_url,
            "website_sale_hide_no_variant_attributes",
            login="admin",
        )
