# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class TestRestrictPartnerProduct(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Portal User",
                    "login": "portal_user@test.com",
                    "email": "portal_user@test.com",
                    "groups_id": [(6, 0, [cls.env.ref("base.group_portal").id])],
                    "password": "portal",
                }
            )
        )
        cls.portal_partner = cls.portal_user.partner_id
        cls.product_tmpl_1 = cls.env["product.template"].create(
            {"name": "Test Product 1", "list_price": 100.0, "is_published": True}
        )
        cls.product_tmpl_2 = cls.env.ref("product.consu_delivery_02").product_tmpl_id

        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Portal Pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_tmpl_1.id,
                            "fixed_price": 90.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_tmpl_2.id,
                            "fixed_price": 180.0,
                        },
                    ),
                ],
            }
        )

    # Set the parameter to True
    def test_restrict_products_param_enabled(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_restrict_by_pricelist.restrict_products", "True"
        )
        # Refresh computed field
        self.portal_partner.invalidate_cache()
        self.assertTrue(
            bool(self.portal_partner.restrict_products_for_all_users),
            "Expected False when restrict_products is enabled",
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_restrict_by_pricelist.restrict_products", ""
        )
        # Refresh computed field
        self.portal_partner.invalidate_cache()
        self.assertFalse(
            bool(self.portal_partner.restrict_products_for_all_users),
            "Expected True when restrict_products is disabled",
        )

    def test_portal_user_sees_products(self):
        self.authenticate("portal_user@test.com", "portal")
        response = self.url_open("/shop")
        content = response.content.decode("utf-8")
        self.assertNotIn("Test Product 1", content)
        self.assertNotIn(self.product_tmpl_2.name, content)
        self.portal_user.property_product_pricelist = self.pricelist.id
        self.env["ir.config_parameter"].sudo().set_param(
            "website_sale_restrict_by_pricelist.restrict_products", "True"
        )
        response = self.url_open("/shop")
        content = response.content.decode("utf-8")
        self.assertIn("Test Product 1", content)
        self.assertIn(self.product_tmpl_2.name, content)

    def test_admin_user_see_all_products(self):
        self.authenticate("admin", "admin")
        response = self.url_open("/shop")
        content = response.content.decode("utf-8")
        self.assertIn(
            self.env.ref("product.product_product_4_product_template").name, content
        )
        self.assertIn(self.env.ref("product.product_product_7").name, content)
