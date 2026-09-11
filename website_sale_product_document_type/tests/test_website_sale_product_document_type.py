# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.tests import HttpCase, tagged

FAKE_CONTENT = base64.b64encode(b"fake document content")


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductDocumentTypeHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.template"]
        cls.Document = cls.env["product.document"]
        cls.document_type = cls.env.ref("product_document_type.document")
        cls.datasheet_type = cls.env.ref("product_document_type.datasheet")
        cls.sds_type = cls.env.ref("product_document_type.sds")

        cls.product = cls.Product.create(
            {
                "name": "Documented Product",
                "type": "consu",
                "list_price": 10.0,
                "website_published": True,
                "sale_ok": True,
            }
        )
        cls.product_without_shown_documents = cls.Product.create(
            {
                "name": "Undocumented Product",
                "type": "consu",
                "list_price": 10.0,
                "website_published": True,
                "sale_ok": True,
            }
        )

        for document_type, attachment_name in (
            (cls.document_type, "Owner Manual.pdf"),
            (cls.datasheet_type, "Spec Sheet.pdf"),
            (cls.sds_type, "Hazard Sheet.pdf"),
        ):
            cls.Document.create(
                {
                    "name": attachment_name,
                    "datas": FAKE_CONTENT,
                    "res_model": "product.template",
                    "res_id": cls.product.id,
                    "document_type_id": document_type.id,
                    "shown_on_product_page": True,
                }
            )
        cls.Document.create(
            {
                "name": "Notes.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.template",
                "res_id": cls.product.id,
                "shown_on_product_page": True,
            }
        )

    def test_product_documents_grouped_by_type(self):
        self.authenticate(None, None)
        response = self.url_open(self.product.website_url)
        content = response.text
        self.assertIn(">Data Sheet<", content)
        self.assertIn(">Safety Data Sheet<", content)
        self.assertIn(">Document<", content)
        self.assertNotIn(">Documents<", content)
        self.assertIn("Owner Manual.pdf", content)
        self.assertIn("Spec Sheet.pdf", content)
        self.assertIn("Hazard Sheet.pdf", content)
        self.assertIn("Notes.pdf", content)

    def test_no_shown_documents_hides_section(self):
        self.authenticate(None, None)
        response = self.url_open(self.product_without_shown_documents.website_url)
        self.assertNotIn('id="product_documents"', response.text)
