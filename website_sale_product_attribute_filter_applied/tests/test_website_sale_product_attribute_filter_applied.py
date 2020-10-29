# Copyright 2020 - Iván Todorovich
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import odoo.tests


@odoo.tests.tagged("-at_install", "post_install")
class WebsiteSaleHttpCase(odoo.tests.HttpCase):
    def setUp(self):
        super().setUp()
        # Create demo product and attribute values
        self.product_template = self.env["product.template"].create(
            {
                "name": "Château Margaux",
                "website_published": True,
                "list_price": 0,
            }
        )
        self.product_attribute = self.env["product.attribute"].create(
            {
                "name": "Grape Varieties",
            }
        )
        self.product_attribute_value = self.env["product.attribute.value"].create(
            {
                "name": n,
                "attribute_id": self.product_attribute.id,
            }
            for n in ["Cabernet Sauvignon", "Merlot", "Malbec"]
        )
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.product_template.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [(6, 0, self.product_attribute_value.ids)],
            }
        )
        # Activate attribute's filter in /shop. By default it's disabled.
        website = self.env["website"].with_context(website_id=1)
        website.viewref("website_sale.products_attributes").active = True
        # Activate applied filters view
        module_name = "website_sale_product_attribute_filter_applied"
        self.env.ref("%s.products_attributes" % module_name).active = True

    def test_01_remove_applied_filter(self):
        self.start_tour("/shop", "website_sale_product_attribute_filter_applied")
