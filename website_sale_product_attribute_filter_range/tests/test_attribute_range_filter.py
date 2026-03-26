# Copyright 2025 EthicHub
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestAttributeRangeFilter(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "SCA Score",
                "display_type": "range",
                "create_variant": "no_variant",
                "visibility": "visible",
            }
        )
        cls.value_80 = cls.env["product.attribute.value"].create(
            {
                "name": "80",
                "attribute_id": cls.attribute.id,
                "numeric_value": 80.0,
            }
        )
        cls.value_85 = cls.env["product.attribute.value"].create(
            {
                "name": "85",
                "attribute_id": cls.attribute.id,
                "numeric_value": 85.0,
            }
        )
        cls.value_90 = cls.env["product.attribute.value"].create(
            {
                "name": "90",
                "attribute_id": cls.attribute.id,
                "numeric_value": 90.0,
            }
        )
        cls.product_1 = cls.env["product.template"].create(
            {
                "name": "Coffee A",
                "is_published": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.value_80.id])],
                        },
                    )
                ],
            }
        )
        cls.product_2 = cls.env["product.template"].create(
            {
                "name": "Coffee B",
                "is_published": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.value_85.id])],
                        },
                    )
                ],
            }
        )
        cls.product_3 = cls.env["product.template"].create(
            {
                "name": "Coffee C",
                "is_published": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.value_90.id])],
                        },
                    )
                ],
            }
        )

    def test_display_type_range_sets_no_variant(self):
        """Test onchange: display_type='range' forces no_variant."""
        attr = self.env["product.attribute"].new(
            {"name": "Test", "display_type": "range"}
        )
        attr._onchange_display_type_range()
        self.assertEqual(attr.create_variant, "no_variant")

    @mute_logger("odoo.sql_db")
    def test_display_type_range_constraint(self):
        """Test constraint: range + create_variant != no_variant."""
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.env["product.attribute"].create(
                {
                    "name": "Bad Range",
                    "display_type": "range",
                    "create_variant": "always",
                }
            )

    def test_parse_numeric_value(self):
        """Test numeric value parsing from attribute value names."""
        AttribValue = self.env["product.attribute.value"]
        self.assertEqual(AttribValue._parse_numeric_value("80"), 80.0)
        self.assertEqual(AttribValue._parse_numeric_value("85.5"), 85.5)
        self.assertEqual(AttribValue._parse_numeric_value("Score: 82"), 82.0)
        self.assertEqual(AttribValue._parse_numeric_value("84,5"), 84.5)
        self.assertIsNone(AttribValue._parse_numeric_value("N/A"))
        self.assertIsNone(AttribValue._parse_numeric_value(""))
        self.assertIsNone(AttribValue._parse_numeric_value(None))

    def test_onchange_name_set_numeric_value(self):
        """Test onchange: name with number sets numeric_value for range attrs."""
        val = self.env["product.attribute.value"].new(
            {
                "name": "Score 87.5",
                "attribute_id": self.attribute.id,
            }
        )
        val._onchange_name_set_numeric_value()
        self.assertEqual(val.numeric_value, 87.5)

        # Non-range attribute should not auto-set
        non_range_attr = self.env["product.attribute"].create(
            {"name": "Color", "display_type": "color"}
        )
        val2 = self.env["product.attribute.value"].new(
            {
                "name": "Red 100",
                "attribute_id": non_range_attr.id,
            }
        )
        val2._onchange_name_set_numeric_value()
        self.assertFalse(val2.numeric_value)

    def test_search_get_detail_filters_by_range(self):
        """Test that range filter adds domain on attribute values."""
        website = self.env["website"].get_current_website()
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayExtraDetail": True,
            "displayExtraLink": True,
            "displayImage": True,
            "allowFuzzy": True,
            "category": None,
            "tags": None,
            "min_price": 0,
            "max_price": 0,
            "attribute_value_dict": {},
            "display_currency": None,
            "attrib_range_dict": {
                self.attribute.id: (82.0, 88.0),
            },
        }
        result = self.env["product.template"]._search_get_detail(
            website, "name asc", options
        )
        domain = result["base_domain"]
        flat_domain = [item for sublist in domain for item in sublist]
        self.assertTrue(
            any(
                item[0] == "attribute_line_ids.value_ids"
                for item in flat_domain
                if isinstance(item, list | tuple) and len(item) == 3
            ),
            "Domain should filter by attribute value IDs",
        )

    def test_search_get_detail_without_range(self):
        """Test _search_get_detail without range params doesn't add domain."""
        website = self.env["website"].get_current_website()
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayExtraDetail": True,
            "displayExtraLink": True,
            "displayImage": True,
            "allowFuzzy": True,
            "category": None,
            "tags": None,
            "min_price": 0,
            "max_price": 0,
            "attribute_value_dict": {},
            "display_currency": None,
            "attrib_range_dict": {},
        }
        result = self.env["product.template"]._search_get_detail(
            website, "name asc", options
        )
        domain = result["base_domain"]
        flat_domain = [item for sublist in domain for item in sublist]
        self.assertFalse(
            any(
                item[0] == "attribute_line_ids.value_ids"
                for item in flat_domain
                if isinstance(item, list | tuple) and len(item) == 3
            ),
        )

    def test_search_get_detail_min_only(self):
        """Test _search_get_detail with only min_val set."""
        website = self.env["website"].get_current_website()
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayExtraDetail": True,
            "displayExtraLink": True,
            "displayImage": True,
            "allowFuzzy": True,
            "category": None,
            "tags": None,
            "min_price": 0,
            "max_price": 0,
            "attribute_value_dict": {},
            "display_currency": None,
            "attrib_range_dict": {
                self.attribute.id: (82.0, 0.0),
            },
        }
        result = self.env["product.template"]._search_get_detail(
            website, "name asc", options
        )
        domain = result["base_domain"]
        flat_domain = [item for sublist in domain for item in sublist]
        self.assertTrue(
            any(
                item[0] == "attribute_line_ids.value_ids"
                for item in flat_domain
                if isinstance(item, list | tuple) and len(item) == 3
            ),
        )

    def test_parse_attrib_ranges(self):
        """Test URL parameter parsing for range filters."""
        from ..controllers.main import WebsiteSaleAttributeRange

        result = WebsiteSaleAttributeRange._parse_attrib_ranges(
            ["5-80.0-90.0", "8-1000-2000"]
        )
        self.assertEqual(result, {5: (80.0, 90.0), 8: (1000.0, 2000.0)})

        # Invalid format
        result = WebsiteSaleAttributeRange._parse_attrib_ranges(["invalid", "5-80"])
        self.assertEqual(result, {})

        # ValueError: non-numeric parts
        result = WebsiteSaleAttributeRange._parse_attrib_ranges(["abc-def-ghi"])
        self.assertEqual(result, {})

        # Empty min/max values
        result = WebsiteSaleAttributeRange._parse_attrib_ranges(["5--"])
        self.assertEqual(result, {5: (0.0, 0.0)})

        # Empty list
        result = WebsiteSaleAttributeRange._parse_attrib_ranges([])
        self.assertEqual(result, {})


@tagged("post_install", "-at_install")
class TestAttributeRangeFilterHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "SCA Score",
                "display_type": "range",
                "create_variant": "no_variant",
                "visibility": "visible",
                "website_range_step": 0.5,
            }
        )
        cls.value_80 = cls.env["product.attribute.value"].create(
            {
                "name": "80",
                "attribute_id": cls.attribute.id,
                "numeric_value": 80.0,
            }
        )
        cls.value_90 = cls.env["product.attribute.value"].create(
            {
                "name": "90",
                "attribute_id": cls.attribute.id,
                "numeric_value": 90.0,
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Range Coffee",
                "is_published": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.value_80.id])],
                        },
                    )
                ],
            }
        )

    def test_shop_without_range_filter(self):
        """Test /shop renders without range filter params."""
        response = self.url_open("/shop")
        self.assertEqual(response.status_code, 200)

    def test_shop_with_range_filter(self):
        """Test /shop with attrib_range param filters products."""
        url = "/shop?attrib_range=%d-78.0-82.0" % self.attribute.id
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Range Coffee", response.text)

    def test_shop_with_range_filter_excludes(self):
        """Test /shop with attrib_range excluding the product."""
        url = "/shop?attrib_range=%d-85.0-90.0" % self.attribute.id
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Range Coffee", response.text)

    def test_shop_with_clamped_range(self):
        """Test /shop with range values outside available bounds."""
        url = "/shop?attrib_range=%d-999.0-1.0" % self.attribute.id
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
