# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.osv import expression
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestProductCatalogPublicCategory(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        category_model = cls.env["product.public.category"]
        cls.drinks = category_model.create({"name": "Test Drinks"})
        cls.wine = category_model.create(
            {"name": "Test Wine", "parent_id": cls.drinks.id}
        )
        cls.beer = category_model.create(
            {"name": "Test Beer", "parent_id": cls.drinks.id}
        )
        cls.gifts = category_model.create({"name": "Test Gifts"})
        cls.tools = category_model.create({"name": "Test Tools"})
        cls.test_categories = cls.drinks | cls.wine | cls.beer | cls.gifts | cls.tools
        product_model = cls.env["product.product"]
        cls.red_wine = product_model.create(
            {
                "name": "Test Red Wine",
                "public_categ_ids": [(6, 0, (cls.wine | cls.gifts).ids)],
            }
        )
        cls.rose_wine = product_model.create(
            {"name": "Test Rose Wine", "public_categ_ids": [(6, 0, cls.wine.ids)]}
        )
        cls.corkscrew = product_model.create(
            {
                "name": "Test Corkscrew",
                "sale_ok": False,
                "public_categ_ids": [(6, 0, cls.tools.ids)],
            }
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _open_catalog(self):
        action = self.order.action_add_from_catalog()
        search_view_id = action["search_view_id"][0]
        views = self.env["product.product"].get_views([(search_view_id, "search")])
        return action, etree.fromstring(views["views"]["search"]["arch"])

    def _load_panel_values(self, search=None):
        # Same call as the search panel of the web client, which adds the
        # search bar terms to the action domain and takes the limit from
        # the view
        action, arch = self._open_catalog()
        panel_field = arch.find("searchpanel/field[@name='public_categ_id']")
        search_domain = action["domain"]
        if search:
            search_domain = expression.AND([search_domain, [("name", "ilike", search)]])
        result = self.env["product.product"].search_panel_select_range(
            "public_categ_id",
            category_domain=[],
            enable_counters=False,
            expand=False,
            filter_domain=[],
            hierarchize=True,
            limit=int(panel_field.get("limit", 200)),
            search_domain=search_domain,
        )
        self.assertNotIn("error_msg", result)
        self.assertEqual(result["parent_field"], "parent_id")
        return result["values"]

    def _load_panel_categories(self, search=None):
        category_ids = {value["id"] for value in self._load_panel_values(search)}
        return self.test_categories.filtered(lambda c: c.id in category_ids)

    def test_search_panel_fields(self):
        _action, arch = self._open_catalog()
        panel = arch.find("searchpanel")
        self.assertEqual(panel.find("field[@name='categ_id']").get("invisible"), "1")
        self.assertIsNotNone(panel.find("field[@name='public_categ_id']"))

    def test_categories_with_products_to_show(self):
        # Beer has no products and the only Tools product cannot be sold
        self.assertEqual(
            self._load_panel_categories(),
            self.drinks | self.wine | self.gifts,
        )
        self.assertEqual(
            self._load_panel_categories(search="Test Rose"),
            self.drinks | self.wine,
        )

    def test_category_names(self):
        # The tree shows each category under its parent with its own name,
        # while the full path is kept everywhere else
        names = {
            value["id"]: value["display_name"] for value in self._load_panel_values()
        }
        self.assertEqual(names[self.wine.id], "Test Wine")
        self.assertEqual(names[self.drinks.id], "Test Drinks")
        self.assertEqual(self.wine.display_name, "Test Drinks / Test Wine")

    def test_many_categories(self):
        # More categories than the default limit of the search panel
        categories = self.env["product.public.category"].create(
            [{"name": f"Test Many {index:03}"} for index in range(201)]
        )
        self.env["product.product"].create(
            {"name": "Test Sampler", "public_categ_ids": [(6, 0, categories.ids)]}
        )
        values = self._load_panel_values()
        self.assertTrue(set(categories.ids) <= {value["id"] for value in values})

    def test_select_category(self):
        action, _arch = self._open_catalog()
        product_model = self.env["product.product"]
        wines = self.red_wine | self.rose_wine
        for category, products in (
            (self.drinks, wines),
            (self.wine, wines),
            (self.gifts, self.red_wine),
            (self.beer, product_model),
            (self.tools, product_model),
        ):
            # Domain the web client builds when the category is selected
            domain = expression.AND(
                [action["domain"], [("public_categ_id", "child_of", category.id)]]
            )
            self.assertEqual(product_model.search(domain), products)
