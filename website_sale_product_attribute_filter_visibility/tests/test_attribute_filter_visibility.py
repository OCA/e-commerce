# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase
from lxml import etree


class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super(WebsiteSaleHttpCase, self).setUp()
        with self.cursor() as cr:
            env = self.env(cr)
            self.attribute_color = env['product.attribute'].create({
                'name': 'test_color',
                'create_variant': False,
                'website_published': True,
                'type': 'radio',
            })
            self.attribute_size = env['product.attribute'].create({
                'name': 'test_size',
                'create_variant': False,
                'type': 'radio',
            })
            self.color_red = env['product.attribute.value'].create({
                'name': 'Red',
                'attribute_id': self.attribute_color.id,
            })
            self.color_blue = env['product.attribute.value'].create({
                'name': 'Blue',
                'attribute_id': self.attribute_color.id,
            })
            self.color_blue = env['product.attribute.value'].create({
                'name': 'Yellow',
                'attribute_id': self.attribute_color.id,
            })
            self.size_large = env['product.attribute.value'].create({
                'name': 'Large',
                'attribute_id': self.attribute_size.id,
            })
            self.size_small = env['product.attribute.value'].create({
                'name': 'Small',
                'attribute_id': self.attribute_size.id,
            })

            self.product = env['product.template'].create({
                'name': 'Test Product',
                'attribute_line_ids': [
                    (0, 0, {
                        'attribute_id': self.attribute_color.id,
                        'value_ids':
                            [(6, 0, [self.color_blue.id, self.color_red.id])],
                    }),
                    (0, 0, {
                        'attribute_id': self.attribute_size.id,
                        'value_ids':
                            [(6, 0, [self.size_small.id, self.size_large.id])],
                    }),
                ],
                'website_published': True,
            })

    def _active_product_filter_view(self):
        with self.cursor() as cr:
            env = self.env(cr)
            # Active the view Product Attributes Filter
            view = env['ir.ui.view'].search([
                ('key', '=', 'website_sale.products_attributes'),
                ('active', '=', False),
            ])
            view.active = True

    def test_render_shop_one_attribute(self):
        self._active_product_filter_view()
        res = self.url_open('/shop', timeout=30)
        tree = etree.fromstring(res.text, parser=etree.HTMLParser())
        attribute_values = len(tree.xpath(
            "//form[@class='js_attributes']//input[@name='attrib']"))
        self.assertEqual(attribute_values, 3)

    def test_render_shop_all_attribute(self):
        self._active_product_filter_view()
        with self.cursor():
            self.attribute_size.website_published = True
        res = self.url_open('/shop', timeout=30)
        tree = etree.fromstring(res.text, parser=etree.HTMLParser())
        attribute_values = len(tree.xpath(
            "//form[@class='js_attributes']//input[@name='attrib']"))
        self.assertEqual(attribute_values, 5)
