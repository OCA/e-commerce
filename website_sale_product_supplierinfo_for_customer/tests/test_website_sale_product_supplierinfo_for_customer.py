from odoo.tests import SavepointCase


class TestWebsiteSaleProductSupplierInfoForCustomer(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResUsers = cls.env["res.users"]
        cls.ResPartner = cls.env["res.partner"]
        cls.ProductTemplate = cls.env["product.template"]
        cls.Product = cls.env["product.product"]
        cls.CustomerInfo = cls.env["product.customerinfo"]

        cls.user_admin = cls.env.ref("base.user_admin")
        cls.partner_admin = cls.user_admin.partner_id

        cls.user_test = cls.ResUsers.create(
            {
                "name": "Test User",
                "login": "test1",
            }
        )
        cls.partner_test = cls.user_test.partner_id

        cls.test_product = cls.Product.create(
            {
                "name": "Test Product",
                "list_price": 20,
            }
        )

        cls.test_product_template = cls.test_product.product_tmpl_id

        cls.test_product_template.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.partner_test.id,
                            "product_id": cls.test_product.id,
                            "product_name": "Test Product Custom Name",
                            "min_qty": 1,
                            "price": 123,
                        },
                    )
                ]
            }
        )

    def _get_partner_price(self, partner, product_template):
        return product_template.with_context({"partner": partner}).price_compute(
            "partner"
        )[product_template.id]

    def test_get_customerinfo_name(self):
        admin_product_name = self.test_product_template._get_customerinfo_name(
            self.partner_admin
        )
        partner_product_name = self.test_product_template._get_customerinfo_name(
            self.partner_test
        )

        self.assertNotEqual(admin_product_name, partner_product_name)

        admin_product_name = self.test_product_template._get_customerinfo_name(
            self.partner_admin, self.test_product
        )
        partner_product_name = self.test_product_template._get_customerinfo_name(
            self.partner_test, self.test_product
        )

        self.assertNotEqual(admin_product_name, partner_product_name)

    def test_price_compute(self):
        admin_price = self._get_partner_price(
            self.partner_admin, self.test_product_template
        )
        test_price = self._get_partner_price(
            self.partner_test, self.test_product_template
        )
        self.assertNotEqual(admin_price, test_price)

    def test_get_combination_info(self):
        combination_test = self.test_product_template.with_user(
            self.user_test
        )._get_combination_info()
        combination_admin = self.test_product_template.with_user(
            self.user_admin
        )._get_combination_info()

        self.assertNotEqual(combination_test, combination_admin)
