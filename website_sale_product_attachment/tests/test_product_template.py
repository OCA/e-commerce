import unittest

from odoo.tests.common import TransactionCase

from odoo.addons.website.models import ir_http


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "Test Product",
            }
        )
        cls.website = cls.env["website"].create(
            {
                "name": "Test Website",
            }
        )

    def test_domain_website_attachment_ids(self):
        with unittest.mock.patch(
            "odoo.addons.website.models.ir_http.get_request_website", return_value=True
        ):
            temporary_patch = False
            if not hasattr(ir_http, "get_current_website"):
                temporary_patch = True
                ir_http.get_current_website = lambda *args, **kwargs: self.website
            try:
                domain = self.product_template._domain_website_attachment_ids()
            finally:
                if temporary_patch:
                    delattr(ir_http, "get_current_website")
        self.assertIn(("public", "=", True), domain)
        self.assertIn(("name", "=ilike", "%.assets%.js"), domain)
        self.assertIn(("name", "=ilike", "%.assets%.css"), domain)
        self.assertIn(("name", "=ilike", "web_editor%"), domain)
        self.assertIn(("name", "=ilike", "/web/content/%.assets%.js"), domain)
        self.assertIn(("name", "=ilike", "/web/content/%.assets%.css"), domain)
        self.assertIn(
            ("name", "=ilike", r"/web/content/%/web\_editor.summernote%.js"), domain
        )
        self.assertIn(
            ("name", "=ilike", r"/web/content/%/web\_editor.summernote%.css"), domain
        )
        clause = next(
            (c for c in domain if isinstance(c, tuple) and c[0] == "website_id"), None
        )
        self.assertIsNotNone(
            clause, "No se encontró la cláusula 'website_id' en el dominio"
        )
        self.assertEqual(
            clause,
            ("website_id", "in", (False, 1)),
            f"La cláusula 'website_id' no es la esperada: {clause}",
        )
