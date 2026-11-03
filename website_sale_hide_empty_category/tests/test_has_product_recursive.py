from odoo.tests import common


class TestPublicCategory(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

    def test_has_product_recursive(self):
        category_1 = self.env["product.public.category"].create({"name": "Category 1"})

        self.assertFalse(category_1.has_product_recursive)

        category_2 = self.env["product.public.category"].create(
            {"name": "Category 2", "parent_id": category_1.id}
        )

        self.assertFalse(category_2.has_product_recursive)

        self.env["product.template"].create(
            {"name": "Product Test", "public_categ_ids": [(4, category_2.id, None)]}
        )

        self.assertTrue(category_1.has_product_recursive)
        self.assertTrue(category_2.has_product_recursive)

    def test_has_product_recursive_website_visitor(self):
        website = self.env["website"].get_current_website()
        other_website = self.env["website"].create({"name": "Other website"})
        category_model = self.env["product.public.category"]
        parent = category_model.create({"name": "Parent"})
        child = category_model.create({"name": "Child", "parent_id": parent.id})
        sibling = category_model.create({"name": "Sibling", "parent_id": parent.id})
        other_category = category_model.create(
            {"name": "Other website category", "website_id": other_website.id}
        )
        product = self.env["product.template"].create(
            {"name": "Not published yet", "public_categ_ids": [(4, child.id)]}
        )
        self.env["product.template"].create(
            [
                {
                    "name": "Other website product",
                    "is_published": True,
                    "website_id": other_website.id,
                    "public_categ_ids": [(4, sibling.id)],
                },
                {
                    "name": "Product in other website category",
                    "is_published": True,
                    "public_categ_ids": [(4, other_category.id)],
                },
            ]
        )
        visitor = website.user_id
        categories = (parent | child | sibling | other_category).with_user(visitor)
        shop = categories.with_context(website_id=website.id)
        other_shop = categories.with_context(website_id=other_website.id)
        self.assertEqual(shop.filtered("has_product_recursive"), shop.browse())
        self.assertEqual(
            other_shop.filtered("has_product_recursive"),
            other_shop.browse([parent.id, sibling.id, other_category.id]),
        )
        # Publishing the product refreshes the categories already read
        product.is_published = True
        self.assertEqual(
            shop.filtered("has_product_recursive"),
            shop.browse([parent.id, child.id]),
        )
