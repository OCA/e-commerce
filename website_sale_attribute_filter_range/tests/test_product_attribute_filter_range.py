# Copyright 2025 Studio73 - Vicent Castells <vicent@studio73.es>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProductAttributeRange(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Attribute = cls.env["product.attribute"]

    def test_display_type_field_has_range_option(self):
        fields_info = self.Attribute.fields_get(["display_type"])
        self.assertIn("display_type", fields_info, "El campo 'display_type' no existe")

        selection = fields_info["display_type"].get("selection") or []
        self.assertIn(
            ("range", "Range"),
            selection,
            "La opción ('range', 'Range') no está en la selección de display_type",
        )

    def test_create_attribute_with_display_type_range(self):
        attr = self.Attribute.create(
            {
                "name": "Size Range",
                "display_type": "range",
            }
        )
        self.assertTrue(attr, "No se pudo crear el product.attribute")
        self.assertEqual(
            attr.display_type,
            "range",
            "El valor de display_type no se guardó como 'range'",
        )
