from unittest.mock import MagicMock, patch

from odoo.http import request
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProductTemplateMinimalPrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].get_current_website()
        cls.category = cls.env["product.category"].create({"name": "Test Category"})
        cls.sub_category = cls.env["product.category"].create(
            {"name": "Sub Category", "parent_id": cls.category.id}
        )
        cls.attribute = cls.env["product.attribute"].create(
            {"name": "Test Attribute", "create_variant": "always"}
        )
        cls.val1 = cls.env["product.attribute.value"].create(
            {"name": "Value 1", "attribute_id": cls.attribute.id}
        )
        cls.val2 = cls.env["product.attribute.value"].create(
            {"name": "Value 2", "attribute_id": cls.attribute.id}
        )
        cls.product_tmpl = cls.env["product.template"].create(
            {
                "name": "Test Product Minimal Price",
                "is_published": True,
                "list_price": 100.0,
                "categ_id": cls.sub_category.id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [(6, 0, [cls.val1.id, cls.val2.id])],
                        },
                    )
                ],
            }
        )

        cls.variant1 = cls.product_tmpl.product_variant_ids[0]
        cls.variant2 = cls.product_tmpl.product_variant_ids[1]

    def test_get_website_current_pricelist(self):
        from odoo.addons.website_sale.tests.common import MockRequest

        with MockRequest(self.env, website=self.website):
            request.pricelist = MagicMock()
            res = self.product_tmpl._get_website_current_pricelist()
            self.assertEqual(res, request.pricelist)
        with patch.object(
            type(self.website), "_get_and_cache_current_pricelist"
        ) as mock_get_cache:
            mock_get_cache.return_value = self.env["product.pricelist"].create(
                {"name": "Cache Pricelist"}
            )
            res = self.product_tmpl._get_website_current_pricelist(self.website)
            self.assertEqual(res, mock_get_cache.return_value)

    def test_pricelist_subpricelists_cycle(self):
        pl1 = self.env["product.pricelist"].create({"name": "PL1"})
        pl2 = self.env["product.pricelist"].create({"name": "PL2"})

        def mock_subpricelists(pricelist):
            if pricelist == pl1:
                return pl2
            return pl1

        with patch.object(
            type(self.product_tmpl),
            "_get_product_subpricelists",
            side_effect=mock_subpricelists,
        ):
            res = self.product_tmpl._get_pricelist_variant_items(pl1)
            self.assertFalse(res)

    def test_cheapest_info_with_variant_items(self):
        pl = self.env["product.pricelist"].create(
            {
                "name": "Cheapest PL",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": self.variant1.id,
                            "compute_price": "fixed",
                            "fixed_price": 50.0,
                        },
                    )
                ],
            }
        )
        product, qty, distinct = self.product_tmpl._get_cheapest_info(pl)
        self.assertEqual(product, self.variant1)
        self.assertTrue(distinct)

    def test_first_possible_combination(self):
        with patch.object(type(self.product_tmpl), "_get_cheapest_info") as mock_cheap:
            mock_cheap.return_value = (self.variant1, 1, True)
            with patch.object(
                type(self.variant1),
                "valid_product_template_attribute_line_ids",
                new=self.product_tmpl.valid_product_template_attribute_line_ids,
            ):
                with patch.object(
                    type(self.variant1),
                    "product_template_attribute_value_ids",
                    new=self.env["product.template.attribute.value"],
                ):
                    res = self.product_tmpl.with_context(
                        website_id=self.website.id
                    )._get_first_possible_combination()
                    self.assertTrue(res)

    def test_combination_info_lines(self):
        from odoo.addons.website_sale.tests.common import MockRequest

        with MockRequest(self.env, website=self.website):
            res = self.product_tmpl._get_combination_info(
                only_template=True, product_id=False
            )
            self.assertIn("price", res)
            res2 = self.product_tmpl._get_combination_info(
                only_template=True, product_id=self.variant1.id
            )
            self.assertIn("price", res2)
            combo = self.variant2.product_template_attribute_value_ids
            res3 = self.product_tmpl._get_combination_info(
                combination=combo, product_id=self.variant1.id
            )
            self.assertEqual(res3["product_id"], self.variant2.id)
            empty_combo = self.env["product.template.attribute.value"].search(
                [("id", "=", 99999999)]
            )  # Empty recordset
            with patch.object(
                type(self.product_tmpl),
                "_get_variant_for_combination",
                return_value=self.env["product.product"],
            ):
                res4 = self.product_tmpl._get_combination_info(combination=empty_combo)
                self.assertIn("price", res4)  # Returns early
            scale_pl = self.env["product.pricelist"].create(
                {
                    "name": "Scale PL",
                    "item_ids": [
                        (
                            0,
                            0,
                            {
                                "applied_on": "1_product",
                                "product_tmpl_id": self.product_tmpl.id,
                                "min_quantity": 5,
                                "compute_price": "fixed",
                                "fixed_price": 80.0,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "applied_on": "1_product",
                                "product_tmpl_id": self.product_tmpl.id,
                                "min_quantity": 10,
                                "compute_price": "fixed",
                                "fixed_price": 70.0,
                            },
                        ),
                    ],
                }
            )
            res5 = self.product_tmpl.with_context(
                pricelist=scale_pl.id
            )._get_combination_info(product_id=self.variant1.id)
            self.assertIn("minimal_price_scale", res5)
            self.assertTrue(len(res5["minimal_price_scale"]) > 0)
