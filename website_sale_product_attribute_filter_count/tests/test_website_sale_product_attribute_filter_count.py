# Copyright 2020 - Iván Todorovich
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from lxml import etree

import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class WebsiteSaleHttpCase(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        # Create demo product and attribute values
        self.product_attribute = self.env["product.attribute"].create(
            {
                "name": "Vintage",
            }
        )
        self.product_attribute_values = self.env["product.attribute.value"].create(
            {
                "name": n,
                "attribute_id": self.product_attribute.id,
            }
            for n in ["2018", "2017", "2016", "2015"]
        )
        self.product_template_1 = self.env["product.template"].create(
            {
                "name": "Château Margaux",
                "website_published": True,
                "list_price": 0,
            }
        )
        self.product_template_2 = self.env["product.template"].create(
            {
                "name": "Château Rouge",
                "website_published": True,
                "list_price": 0,
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.product_template_1.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [(6, 0, self.product_attribute_values[:-1].ids)],
            }
        )
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.product_template_2.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [(6, 0, self.product_attribute_values[:-2].ids)],
            }
        )
        # Website views
        module_name = "website_sale_product_attribute_filter_count"
        self.view_existing_ref = "%s.products_attributes_existing" % module_name
        self.view_count_ref = "%s.products_attributes_count" % module_name
        self.website = self.env["website"].with_context(website_id=1)
        # Activate attribute's filter in /shop. By default it's disabled.
        self.website.viewref("website_sale.products_attributes").active = True

    def test_01_product_attribute_filter_count(self):
        # Activate custom views
        self.website.viewref(self.view_count_ref).active = True
        # Open shop
        res = self.url_open("/shop")
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content, etree.HTMLParser())
        # Check that count for '2018' is correct
        span = root.xpath(
            '//div[@id="wsale_products_attributes_collapse"]'
            '//span[contains(text(), "2018")]'
            "/.."
            '/span[hasclass("attribute-variant-count")]'
        )
        count = etree.tostring(span[0], encoding="unicode", method="text")
        count = count.replace(" ", "").replace("\n", "")
        self.assertEqual(count, "2", "Count for '2018' vintage should be 2")
        # Check that count for '2016' is correct
        span = root.xpath(
            '//div[@id="wsale_products_attributes_collapse"]'
            '//span[contains(text(), "2016")]'
            "/.."
            '/span[hasclass("attribute-variant-count")]'
        )
        count = etree.tostring(span[0], encoding="unicode", method="text")
        count = count.replace(" ", "").replace("\n", "")
        self.assertEqual(count, "1", "Count for '2016' vintage should be 1")

    def test_02_product_attribute_filter_existing(self):
        # Activate custom view
        self.website.viewref(self.view_existing_ref).active = True
        # Open shop
        res = self.url_open("/shop")
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content, etree.HTMLParser())
        # Check that unavailable '2015' attribute value is not shown
        span = root.xpath(
            '//div[@id="wsale_products_attributes_collapse"]'
            '//span[contains(text(), "2015")]'
        )
        self.assertEqual(len(span), 0)
        # Deactivate custom view
        self.website.viewref(self.view_existing_ref).active = False
        # Open shop
        res = self.url_open("/shop")
        self.assertEqual(res.status_code, 200)
        root = etree.fromstring(res.content, etree.HTMLParser())
        # Check that unavailable '2015' attribute value is shown
        span = root.xpath(
            '//div[@id="wsale_products_attributes_collapse"]'
            '//span[contains(text(), "2015")]'
        )
        self.assertEqual(len(span), 1)
