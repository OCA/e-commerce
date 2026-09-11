# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.tests import TransactionCase, tagged

FAKE_CONTENT = base64.b64encode(b"fake document content")


@tagged("-at_install", "post_install")
class TestWebsiteSaleProductDocumentTypeVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.document_type = cls.env.ref("product_document_type.document")
        cls.datasheet_type = cls.env.ref("product_document_type.datasheet")
        cls.product = cls.env["product.template"].create(
            {"name": "Documented Product", "type": "consu"}
        )
        cls.variant = cls.product.product_variant_ids[:1]
        cls.env["product.document"].create(
            {
                "name": "Owner Manual.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.template",
                "res_id": cls.product.id,
                "document_type_id": cls.document_type.id,
                "shown_on_product_page": True,
            }
        )
        cls.env["product.document"].create(
            {
                "name": "Variant Spec Sheet.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.product",
                "res_id": cls.variant.id,
                "document_type_id": cls.datasheet_type.id,
                "shown_on_product_page": True,
            }
        )

    def test_variant_documents_html_grouped_by_type(self):
        html = self.product._get_variant_documents_html(self.variant)

        self.assertIn(">Document<", html)
        self.assertIn(">Data Sheet<", html)
        self.assertIn("Owner Manual.pdf", html)
        self.assertIn("Variant Spec Sheet.pdf", html)
        self.assertNotIn(">Documents<", html)
