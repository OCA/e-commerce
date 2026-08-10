# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64
from datetime import date

from odoo.fields import Command
from odoo.tests import TransactionCase, tagged
from odoo.tools import format_date

from odoo.addons.website_sale.tests.common import MockRequest

DUMMY_IMAGE = base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8Dw"
        "HwAFAAH/q842iQAAAABJRU5ErkJggg=="
    )
)

NEW_TTYPES = [
    "integer",
    "float",
    "date",
    "datetime",
    "selection",
    "many2one",
    "one2many",
    "many2many",
]


@tagged("post_install", "-at_install")
class TestWebsiteSaleVariantExtraField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        # Start from a clean configuration: the database may already have extra
        # fields configured, which would pollute the payload assertions.
        cls.website.shop_extra_field_ids.unlink()
        cls.attribute = cls.env["product.attribute"].create(
            {"name": "Test Attribute", "create_variant": "always"}
        )
        cls.value_1 = cls.env["product.attribute.value"].create(
            {"name": "Value 1", "attribute_id": cls.attribute.id}
        )
        cls.value_2 = cls.env["product.attribute.value"].create(
            {"name": "Value 2", "attribute_id": cls.attribute.id}
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "is_published": True,
                "list_price": 100.0,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [
                                Command.set([cls.value_1.id, cls.value_2.id])
                            ],
                        }
                    )
                ],
            }
        )
        cls.variant_1, cls.variant_2 = cls.product_tmpl.product_variant_ids[:2]
        cls.variant_1.default_code = "REF-1"
        cls.variant_2.default_code = "REF-2"

    def _create_extra_field(self, model, name):
        field = self.env["ir.model.fields"]._get(model, name)
        self.assertTrue(field, f"No ir.model.fields record for {model}.{name}")
        return self.env["website.sale.extra.field"].create(
            {"website_id": self.website.id, "field_id": field.id}
        )

    def _field_id_domain(self):
        return list(self.env["website.sale.extra.field"]._fields["field_id"].domain)

    def test_field_id_domain_accepts_variants_and_new_types(self):
        domain = self._field_id_domain()
        models = next(cond[2] for cond in domain if cond[0] == "model_id.model")
        self.assertEqual(sorted(models), ["product.product", "product.template"])
        ttypes = next(cond[2] for cond in domain if cond[0] == "ttype")
        for ttype in ["char", "binary"] + NEW_TTYPES:
            self.assertIn(ttype, ttypes)

    def test_field_id_domain_selects_variant_fields(self):
        IrModelFields = self.env["ir.model.fields"]
        selectable = IrModelFields.search(self._field_id_domain())
        self.assertIn(IrModelFields._get("product.product", "default_code"), selectable)
        self.assertIn(IrModelFields._get("product.product", "volume"), selectable)
        self.assertIn(IrModelFields._get("product.template", "name"), selectable)

    def test_is_variant_field(self):
        variant_extra_field = self._create_extra_field(
            "product.product", "default_code"
        )
        template_extra_field = self._create_extra_field("product.template", "name")
        self.assertTrue(variant_extra_field.is_variant_field)
        self.assertFalse(template_extra_field.is_variant_field)

    def test_source_record_depends_on_field_model(self):
        variant_extra_field = self._create_extra_field(
            "product.product", "default_code"
        )
        template_extra_field = self._create_extra_field("product.template", "name")
        self.assertEqual(
            variant_extra_field._get_source_record(self.product_tmpl, self.variant_1),
            self.variant_1,
        )
        self.assertEqual(
            template_extra_field._get_source_record(self.product_tmpl, self.variant_1),
            self.product_tmpl,
        )

    def test_render_char_field(self):
        extra_field = self._create_extra_field("product.product", "default_code")
        self.assertEqual(extra_field._render_value(self.variant_1), "REF-1")

    def test_render_integer_field(self):
        self.variant_1.sequence = 42
        extra_field = self._create_extra_field("product.product", "sequence")
        self.assertEqual(extra_field._render_value(self.variant_1), "42")

    def test_render_float_field_uses_field_digits(self):
        self.env.ref("product.decimal_volume").digits = 3
        self.variant_1.volume = 1.5
        extra_field = self._create_extra_field("product.product", "volume")
        self.assertEqual(extra_field._get_render_options()["precision"], 3)
        self.assertEqual(extra_field._render_value(self.variant_1), "1.500")

    def test_render_date_field(self):
        deadline = date(2026, 1, 15)
        self.env["mail.activity"].create(
            {
                "res_model_id": self.env["ir.model"]._get_id("product.product"),
                "res_id": self.variant_1.id,
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "date_deadline": deadline,
                "summary": "Test activity",
            }
        )
        extra_field = self._create_extra_field(
            "product.product", "activity_date_deadline"
        )
        self.assertEqual(
            extra_field._render_value(self.variant_1),
            format_date(self.env, deadline),
        )

    def test_render_datetime_field(self):
        extra_field = self._create_extra_field("product.product", "create_date")
        rendered = extra_field._render_value(self.variant_1)
        self.assertTrue(rendered)
        self.assertNotEqual(rendered, str(self.variant_1.create_date))

    def test_render_selection_field(self):
        extra_field = self._create_extra_field("product.product", "type")
        rendered = extra_field._render_value(self.variant_1)
        labels = dict(
            self.env["product.product"]
            ._fields["type"]
            .get_description(self.env)["selection"]
        )
        self.assertEqual(rendered, labels[self.variant_1.type])
        # The label is displayed, not the raw technical value.
        self.assertNotEqual(rendered, self.variant_1.type)

    def test_render_many2one_field(self):
        extra_field = self._create_extra_field("product.product", "product_tmpl_id")
        self.assertEqual(
            extra_field._render_value(self.variant_1), self.product_tmpl.display_name
        )

    def test_render_many2many_field(self):
        tags = self.env["product.tag"].create([{"name": "Tag A"}, {"name": "Tag B"}])
        self.variant_1.additional_product_tag_ids = tags
        extra_field = self._create_extra_field(
            "product.product", "additional_product_tag_ids"
        )
        self.assertEqual(extra_field._render_value(self.variant_1), "Tag A, Tag B")

    def test_render_one2many_field(self):
        pricelist_1 = self.env["product.pricelist"].create({"name": "Test Pricelist A"})
        pricelist_2 = self.env["product.pricelist"].create({"name": "Test Pricelist B"})
        rule_1, rule_2 = self.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": pricelist_1.id,
                    "applied_on": "0_product_variant",
                    "product_id": self.variant_1.id,
                    "compute_price": "fixed",
                    "fixed_price": 50.0,
                },
                {
                    "pricelist_id": pricelist_2.id,
                    "applied_on": "0_product_variant",
                    "product_id": self.variant_1.id,
                    "compute_price": "fixed",
                    "fixed_price": 60.0,
                },
            ]
        )
        extra_field = self._create_extra_field("product.product", "pricelist_rule_ids")
        self.assertEqual(
            extra_field._render_value(self.variant_1),
            ", ".join((rule_1 + rule_2).mapped("display_name")),
        )

    def test_render_binary_field(self):
        self.variant_1.image_variant_1920 = DUMMY_IMAGE
        extra_field = self._create_extra_field("product.product", "image_variant_1920")
        self.assertIn(
            f"/web/content/product.product/{self.variant_1.id}"
            "/image_variant_1920?download=1",
            extra_field._render_value(self.variant_1),
        )

    def test_render_empty_value(self):
        self.variant_1.default_code = False
        extra_field = self._create_extra_field("product.product", "default_code")
        self.assertEqual(extra_field._render_value(self.variant_1), "")

    # Requirement 2: recompute on variant change

    def test_combination_info_renders_current_variant_value(self):
        self._create_extra_field("product.product", "default_code")
        with MockRequest(self.env, website=self.website):
            info_1 = self.product_tmpl._get_combination_info(
                product_id=self.variant_1.id
            )
            info_2 = self.product_tmpl._get_combination_info(
                product_id=self.variant_2.id
            )
        self.assertEqual(info_1["variant_extra_fields"], {"default_code": "REF-1"})
        self.assertEqual(info_2["variant_extra_fields"], {"default_code": "REF-2"})

    def test_combination_info_without_variant_extra_field(self):
        self._create_extra_field("product.template", "name")
        with MockRequest(self.env, website=self.website):
            info = self.product_tmpl._get_combination_info(product_id=self.variant_1.id)
        self.assertNotIn("variant_extra_fields", info)

    def test_combination_info_keeps_empty_value_key(self):
        self.variant_2.default_code = False
        self._create_extra_field("product.product", "default_code")
        with MockRequest(self.env, website=self.website):
            info = self.product_tmpl._get_combination_info(product_id=self.variant_2.id)
        # The key must stay in the payload so that the client side refresh can
        # hide the value that is not set on the newly selected variant.
        self.assertEqual(info["variant_extra_fields"], {"default_code": ""})

    def test_block_displayed_for_variant_field_without_value(self):
        self.variant_1.default_code = False
        self._create_extra_field("product.product", "default_code")
        self.assertTrue(
            self.website.shop_extra_field_ids._has_content_to_display(
                self.product_tmpl, self.variant_1
            )
        )

    def test_block_hidden_for_template_field_without_value(self):
        self._create_extra_field("product.template", "image_1920")
        self.assertFalse(
            self.website.shop_extra_field_ids._has_content_to_display(
                self.product_tmpl, self.variant_1
            )
        )

    def test_block_displayed_for_template_field_with_value(self):
        self._create_extra_field("product.template", "name")
        self.assertTrue(
            self.website.shop_extra_field_ids._has_content_to_display(
                self.product_tmpl, self.variant_1
            )
        )
