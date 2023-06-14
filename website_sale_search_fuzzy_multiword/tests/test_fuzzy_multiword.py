from psycopg2 import sql

from odoo.tests.common import TransactionCase


class TestFuzzyMultiWord(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.ResConfigSettings = cls.env["res.config.settings"]
        cls.Website = cls.env["website"].with_context(lang="en_US")

        cls.env.cr.execute(sql.SQL("SELECT show_limit()"))
        cls.db_similarity = cls.env.cr.fetchall()[0][0]

        cls.currency = cls.env["res.currency"].browse(1)
        cls.input_data = {
            "search_type": "products",
            "search": "",
            "limit": 1000,
            "order": "is_published desc, name asc, id desc",
            "options": {
                "allowFuzzy": True,
                "displayDescription": True,
                "displayDetail": True,
                "displayExtraLink": True,
                "displayImage": True,
                "display_currency": cls.currency,
            },
        }

    def test_exact_no_fuzzy_allowed_multi_w(self):
        search = "Four Person Desk"
        self.input_data["search"] = search
        self.input_data["options"]["allowFuzzy"] = False
        total_count, all_results, _ = self.Website._search_with_fuzzy(**self.input_data)
        self.assertEqual(total_count, 1)
        relevant_result = [r for r in all_results if r["count"] > 0][0]
        self.assertEqual(relevant_result["results"].name, search)

    def test_fuzzy_multi_w(self):
        search = "Corner Dess"
        self.input_data["search"] = search
        self.input_data["options"]["allowFuzzy"] = True
        total_count, all_results, fuzzy_term = self.Website._search_with_fuzzy(
            **self.input_data
        )
        relevant_results = [
            r
            for r in all_results
            if r["count"] > 0 and r["model"] == "product.template"
        ]
        expected = ["Corner Desk Left Sit", "Corner Desk Right Sit"]
        self.assertGreaterEqual(total_count, 2)
        for r in relevant_results:
            self.assertIn(r.name, expected)

    def test_postgres_similarity(self):
        identical = self.Website._direct_postgres_similarity("word", "word")
        self.assertEqual(identical, 1.0)
        completely_different = self.Website._direct_postgres_similarity(
            "giraffe", "rhino"
        )
        self.assertEqual(completely_different, 0)
        slightly_different = self.Website._direct_postgres_similarity(
            "wordA1", "wordB2"
        )
        self.assertGreaterEqual(slightly_different, self.db_similarity)
        too_long = self.Website._direct_postgres_similarity("a", "a" * 150)
        self.assertEqual(too_long, 0)
