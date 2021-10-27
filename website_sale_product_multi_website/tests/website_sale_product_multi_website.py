from odoo.tests


class TestWebsiteSaleProductMultiWebsite(tests.HttpCase):

    def setUp(self):
        super().setUp()
        # Create multiple websites
        self.website0 = self.env['website'].create({'name': 'web0'})
        self.website1 = self.env['website'].create({'name': 'web1'})
        self.website2 = self.env['website'].create({'name': 'web2'})

        # create a product template
        self.product_template = self.env['product.template'].create({
            'name': 'Test Product',
            'is_published': True,
            'list_price': 750,
        })

    def test_01(self):
        """ Prueba que si el producto no tiene websites dicho producto esta disponible en todos los websites
        """
