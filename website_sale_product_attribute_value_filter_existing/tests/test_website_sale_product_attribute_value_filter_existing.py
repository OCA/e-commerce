# Copyright 2019 Tecnativa - Sergio Teruel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests.common import HttpCase


class WebsiteSaleHttpCase(HttpCase):
    def setUp(self):
        super().setUp()
        # Models
        ProductAttribute = self.env['product.attribute']
        ProductAttributeValue = self.env['product.attribute.value']
        ProductAttributeLine = self.env['product.template.attribute.line']
        self.product_attribute = ProductAttribute.create({
            'name': 'Test Special Color',
            'website_published': True,
            'create_variant': 'no_variant',
        })
        self.product_attribute_value_red = ProductAttributeValue.create({
            'name': 'Test red',
            'attribute_id': self.product_attribute.id,
        })
        self.product_attribute_value_green = ProductAttributeValue.create({
            'name': 'Test green',
            'attribute_id': self.product_attribute.id,
        })
        self.product_attribute_value_blue = ProductAttributeValue.create({
            'name': 'Test blue',
            'attribute_id': self.product_attribute.id,
        })
        self.product_template = self.env.ref(
            'product.product_product_4_product_template')
        self.product_attribute_line = ProductAttributeLine.create({
            'product_tmpl_id': self.product_template.id,
            'attribute_id': self.product_attribute.id,
            'value_ids': [(6, 0,
                           [self.product_attribute_value_red.id,
                            self.product_attribute_value_green.id]
                           )]
        })
        self.product_template.write({
            'attribute_line_ids': [(4, self.product_attribute_line.id)]
        })
        self.product_template_27 = self.env.ref(
            'product.product_product_27_product_template')
        self.product_attribute_line_27 = ProductAttributeLine.create({
            'product_tmpl_id': self.product_template_27.id,
            'attribute_id': self.product_attribute.id,
            'value_ids': [(6, 0,
                           [self.product_attribute_value_red.id,
                            self.product_attribute_value_blue.id]
                           )]
        })
        self.product_template_27.write({
            'attribute_line_ids': [(4, self.product_attribute_line_27.id)]
        })
        # Active attribute's filter in /shop. By default it's disabled.
        self.env.ref('website_sale.products_attributes').active = True

    def test_ui_website(self):
        """Test frontend tour."""
        tour = (
            "odoo.__DEBUG__.services['web_tour.tour']",
            "website_sale_product_attribute_value_filter_existing",
        )
        self.phantom_js(
            url_path="/",
            code="%s.run('%s')" % tour,
            ready="%s.tours['%s'].ready" % tour,
            login="admin"
        )
