from odoo.tests import TransactionCase, tagged

from odoo.addons.website_sale_firstname.controllers.main import WebsiteSaleFirstname


@tagged("post_install", "-at_install")
class TestWebsiteSaleFirstname(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteSaleController = WebsiteSaleFirstname()

    def test_first_last_in_mandatory_fields(self):
        fields_billing = self.WebsiteSaleController._get_mandatory_fields_billing()

        self.assertTrue("name" not in fields_billing)
        self.assertTrue("firstname" in fields_billing)
        self.assertTrue("lastname" in fields_billing)

        fields_shipping = self.WebsiteSaleController._get_mandatory_fields_shipping()

        self.assertTrue("name" not in fields_shipping)
        self.assertTrue("firstname" in fields_shipping)
        self.assertTrue("lastname" in fields_shipping)
