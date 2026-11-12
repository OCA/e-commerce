# Copyright 2026 Domatix
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import HttpCase, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.website_sale.tests.common import MockRequest


class TestWebsiteSaleProductComparePrice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].create(
            {
                "group_product_pricelist": True,
                "group_product_price_comparison": True,
            }
        ).execute()
        cls.website = cls.env.ref(
            "website.default_website", raise_if_not_found=False
        ) or cls.env["website"].create({"name": "Compare Price Test Website"})
        currency = cls.env.company.currency_id
        cls.product = cls.env["product.template"].create(
            {
                "name": "Compare Price Test Product",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.product_with_compare = cls.env["product.template"].create(
            {
                "name": "Compare Price Test Product Manual",
                "type": "consu",
                "list_price": 100.0,
                "compare_list_price": 150.0,
                "taxes_id": [Command.clear()],
            }
        )
        cls.pricelist_empty = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Empty Pricelist",
                "currency_id": currency.id,
                "selectable": True,
            }
        )
        cls.pricelist_fixed = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Fixed Pricelist",
                "currency_id": currency.id,
                "selectable": True,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 70.0,
                        }
                    )
                ],
            }
        )
        cls.pricelist_discount = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Discount Pricelist",
                "currency_id": currency.id,
                "selectable": True,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.id,
                            "compute_price": "percentage",
                            "percent_price": 10.0,
                        }
                    )
                ],
            }
        )
        cls.tax_group = cls.env["account.tax.group"].create(
            {"name": "Compare Price Test Tax Group"}
        )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Compare Price Test Tax",
                "amount_type": "percent",
                "amount": 10.0,
                "tax_group_id": cls.tax_group.id,
                "type_tax_use": "sale",
            }
        )
        cls.product_with_tax = cls.env["product.template"].create(
            {
                "name": "Compare Price Test Product With Tax",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": [Command.set(cls.tax.ids)],
            }
        )
        cls.pricelist_tax = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Tax Pricelist",
                "currency_id": currency.id,
                "selectable": True,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_with_tax.id,
                            "compute_price": "fixed",
                            "fixed_price": 70.0,
                        }
                    )
                ],
            }
        )
        cls.foreign_currency = cls.env["res.currency"].create(
            {"name": "TES", "symbol": "T"}
        )
        cls.env["res.currency.rate"].create(
            {
                "currency_id": cls.foreign_currency.id,
                "rate": 2.0,
                "company_id": cls.env.company.id,
            }
        )
        cls.product_foreign = cls.env["product.template"].create(
            {
                "name": "Compare Price Test Product Foreign Currency",
                "type": "consu",
                "list_price": 200.0,
                "currency_id": cls.foreign_currency.id,
                "taxes_id": [Command.clear()],
            }
        )
        cls.pricelist_foreign = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Foreign Pricelist",
                "currency_id": cls.foreign_currency.id,
                "selectable": True,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_foreign.id,
                            "compute_price": "fixed",
                            "fixed_price": 100.0,
                        }
                    )
                ],
            }
        )
        cls.pricelist_fixed_small = cls.env["product.pricelist"].create(
            {
                "name": "Compare Price Test Small Discount Pricelist",
                "currency_id": currency.id,
                "selectable": True,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product.id,
                            "compute_price": "fixed",
                            "fixed_price": 99.8,
                        }
                    )
                ],
            }
        )

    def _combination_info(self, product, pricelist):
        with MockRequest(
            self.env,
            website=self.website,
            website_sale_current_pl=pricelist.id,
        ):
            return product.with_context(
                website_id=self.website.id
            )._get_combination_info(product_id=product.product_variant_id.id)

    def test_fixed_pricelist_shows_variant_compare_price(self):
        """A fixed pricelist price shows the variant sales price crossed out
        with the discount badge and the amount saved."""
        info = self._combination_info(self.product, self.pricelist_fixed)
        self.assertTrue(info["has_compare_price"])
        self.assertEqual(info["compare_price"], 100.0)
        self.assertEqual(info["compare_badge_text"], "-30%")
        self.assertTrue(info["compare_save_text"].startswith("You save "))

    def test_manual_compare_list_price_shows_savings(self):
        """The manual *Compare to Price* field shows badge and saved amount,
        keeping the native crossed-out reference."""
        info = self._combination_info(self.product_with_compare, self.pricelist_empty)
        self.assertFalse(info["has_compare_price"])
        self.assertTrue(info["compare_list_price"])
        self.assertEqual(info["compare_badge_text"], "-33%")
        self.assertTrue(info["compare_save_text"].startswith("You save "))

    def test_no_discount_shows_nothing(self):
        """No compare block when the price is not discounted."""
        info = self._combination_info(self.product, self.pricelist_empty)
        self.assertFalse(info["has_compare_price"])
        self.assertFalse(info["compare_badge_text"])
        self.assertFalse(info["compare_save_text"])

    def test_native_discount_is_not_overridden(self):
        """A pricelist discount shown natively keeps its own behaviour."""
        info = self._combination_info(self.product, self.pricelist_discount)
        self.assertTrue(info["has_discounted_price"])
        self.assertFalse(info["has_compare_price"])
        self.assertFalse(info["compare_badge_text"])
        self.assertFalse(info["compare_save_text"])

    def test_fixed_pricelist_applies_taxes_to_compare_price(self):
        """The variant compare price is loaded with the same taxes as the
        sale price."""
        info = self._combination_info(self.product_with_tax, self.pricelist_tax)
        self.assertTrue(info["has_compare_price"])
        self.assertEqual(info["compare_badge_text"], "-30%")
        self.assertTrue(info["compare_save_text"].startswith("You save "))

    def test_fixed_pricelist_in_other_currency(self):
        """The variant sales price is converted to the website currency."""
        info = self._combination_info(self.product_foreign, self.pricelist_foreign)
        self.assertTrue(info["has_compare_price"])
        self.assertTrue(info["compare_price_formatted"])
        self.assertTrue(info["compare_save_text"].startswith("You save "))

    def test_sub_one_percent_discount_is_ignored(self):
        """Reductions below one percent are not displayed."""
        info = self._combination_info(self.product, self.pricelist_fixed_small)
        self.assertFalse(info["has_compare_price"])
        self.assertFalse(info["compare_badge_text"])
        self.assertFalse(info["compare_save_text"])


class TestWebsiteSaleProductComparePriceDisabled(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref(
            "website.default_website", raise_if_not_found=False
        ) or cls.env["website"].create({"name": "Compare Price Disabled Website"})
        cls.product = cls.env["product.template"].create(
            {
                "name": "Compare Price Disabled Product",
                "type": "consu",
                "list_price": 100.0,
                "compare_list_price": 150.0,
            }
        )

    def test_disabled_comparison_price_shows_nothing(self):
        """Nothing is computed when the *Comparison Price* feature is off."""
        with MockRequest(self.env, website=self.website):
            info = self.product.with_context(
                website_id=self.website.id
            )._get_combination_info(product_id=self.product.product_variant_id.id)
        self.assertFalse(info["has_compare_price"])
        self.assertFalse(info["compare_badge_text"])
        self.assertFalse(info["compare_save_text"])


@tagged("post_install", "-at_install")
class WebsiteSaleProductComparePriceUiCase(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env["res.config.settings"].create(
            {"group_product_price_comparison": True}
        ).execute()
        # Minimal 1x1 red PNG.
        image = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGM4oaEBAALUA"
            "RkFUI+kAAAAAElFTkSuQmCC"
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Compare Price Demo Product",
                "type": "consu",
                "sale_ok": True,
                "website_published": True,
                "list_price": 100.0,
                "compare_list_price": 150.0,
                "image_1920": image,
                "taxes_id": [Command.clear()],
            }
        )

    def test_product_page_renders_saved_amount(self):
        """The compare price block is rendered on the product page."""
        response = self.url_open(f"/shop/{self.product.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("oe_compare_price_block", response.text)
        self.assertIn("You save", response.text)

    def test_tour_website(self):
        """Frontend tour: the saved amount is displayed on the product page."""
        self.start_tour("/shop", "website_sale_product_compare_price", login="admin")
