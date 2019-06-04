# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):

    def setUp(self):
        super().setUp()
        Attribute = self.env['product.attribute']
        AttributeValue = self.env['product.attribute.value']

        self.product_attribute_test_color = Attribute.create({
            'website_published': True,
            'name': 'Test Color',
            'create_variant': 'no_variant',
        })
        self.product_attribute_value_color_red = AttributeValue.create({
            'name': 'Test Red',
            'attribute_id': self.product_attribute_test_color.id,
        })
        self.product_attribute_value_color_green = AttributeValue.create({
            'name': 'Test Green',
            'attribute_id': self.product_attribute_test_color.id,
        })
        self.product_attribute_value_color_blue = AttributeValue.create({
            'name': 'Test Blue',
            'attribute_id': self.product_attribute_test_color.id,
        })

        self.product_attribute_test_size = Attribute.create({
            'website_published': False,
            'name': 'Test Size',
            'create_variant': 'no_variant',
        })
        self.product_attribute_value_test_size_small = AttributeValue.create({
            'name': 'Size Small',
            'attribute_id': self.product_attribute_test_size.id,
        })
        self.product_attribute_value_test_size_large = AttributeValue.create({
            'name': 'Size Large',
            'attribute_id': self.product_attribute_test_size.id,
        })
        self.product_template = self.env.ref(
            'product.product_product_4_product_template')
        self.product_template.write({
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': self.product_attribute_test_color.id,
                    'value_ids': [(6, 0, [
                        self.product_attribute_value_color_red.id,
                        self.product_attribute_value_color_green.id])]
                }),
                (0, 0, {
                    'attribute_id': self.product_attribute_test_size.id,
                    'value_ids': [(6, 0, [
                        self.product_attribute_value_test_size_small.id,
                        self.product_attribute_value_test_size_large.id])]
                })]
        })

        # Active attribute's filter in /shop. By default it's disabled.
        self.env.ref('website_sale.products_attributes').active = True

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_product_attribute_filter_visibility",
        )
        self.browser_js(
            url_path="/shop",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin",
        )
