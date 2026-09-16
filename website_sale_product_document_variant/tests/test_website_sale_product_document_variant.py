# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import json
from urllib.parse import urlparse

from lxml import html

from odoo.fields import Command
from odoo.tests import HttpCase, tagged

FAKE_CONTENT = base64.b64encode(b"fake document content")


@tagged("post_install", "-at_install")
class TestWebsiteSaleProductDocumentVariantHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Document = cls.env["product.document"]
        size_attribute = cls.env["product.attribute"].create(
            {
                "name": "Size",
                "value_ids": [
                    Command.create({"name": "Small"}),
                    Command.create({"name": "Large"}),
                ],
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Documented Variant Product",
                "type": "consu",
                "website_published": True,
                "sale_ok": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": size_attribute.id,
                            "value_ids": [Command.set(size_attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        cls.small, cls.large = cls.product.product_variant_ids
        cls.Document.create(
            {
                "name": "General Manual.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.template",
                "res_id": cls.product.id,
                "shown_on_product_page": True,
            }
        )
        cls.small_document = cls.Document.create(
            {
                "name": "Small Size Chart.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.product",
                "res_id": cls.small.id,
                "shown_on_product_page": True,
            }
        )
        cls.product_without_documents = cls.env["product.template"].create(
            {
                "name": "Undocumented Product",
                "type": "consu",
                "website_published": True,
                "sale_ok": True,
            }
        )

    @staticmethod
    def _make_jsonrpc_payload(params):
        return json.dumps({"jsonrpc": "2.0", "method": "call", "params": params})

    def test_variant_and_template_documents_shown_together(self):
        self.authenticate(None, None)
        response = self.url_open(
            f"{self.product.website_url}"
            f"#attribute_values={self.small.product_template_attribute_value_ids.id}"
        )
        content = response.text
        self.assertIn("General Manual.pdf", content)
        self.assertIn("Small Size Chart.pdf", content)

    def test_no_shown_documents_hides_section(self):
        """The container is always rendered (see
        test_container_present_even_without_shown_documents below) but must
        stay visually hidden and empty of document links when the current
        combination has nothing published.

        Scoped to the "#product_documents" node itself: this page also has
        unrelated "list-group" elements elsewhere (e.g. website menus), so a
        page-wide substring check would give a false negative.
        """
        self.authenticate(None, None)
        response = self.url_open(self.product_without_documents.website_url)
        documents_el = html.fromstring(response.content).get_element_by_id(
            "product_documents"
        )
        self.assertIn("d-none", documents_el.get("class", ""))
        self.assertFalse(documents_el.find_class("list-group"))

    def test_container_present_even_without_shown_documents(self):
        """The AJAX refresh JS looks up "#product_documents" by id unconditionally.
        If the container is absent from the initial render whenever
        the starting combination has no documents, switching
        to a variant that does have a published document has no target node
        to inject it into, and the document silently never appears."""
        self.authenticate(None, None)
        response = self.url_open(self.product_without_documents.website_url)
        self.assertIn('id="product_documents"', response.text)

    def test_get_variant_documents_html_recomputes_by_variant(self):
        """`_get_variant_documents_html` must return content matching the
        given variant, so the front-end can refresh the documents section
        when the customer changes variant."""
        html_small = self.product._get_variant_documents_html(self.small)
        html_large = self.product._get_variant_documents_html(self.large)
        self.assertIn("General Manual.pdf", html_small)
        self.assertIn("Small Size Chart.pdf", html_small)
        self.assertIn("General Manual.pdf", html_large)
        self.assertNotIn("Small Size Chart.pdf", html_large)

    def test_get_variant_documents_html_empty_for_no_documents(self):
        html = self.product_without_documents._get_variant_documents_html(
            self.env["product.product"]
        )
        self.assertNotIn("list-group", html)

    def test_get_combination_info_carries_documents_html(self):
        self.authenticate(None, None)
        small_ptav = self.small.product_template_attribute_value_ids
        large_ptav = self.large.product_template_attribute_value_ids
        response_small = self.url_open(
            "/website_sale/get_combination_info",
            data=self._make_jsonrpc_payload(
                {
                    "product_template_id": self.product.id,
                    "product_id": self.small.id,
                    "combination": small_ptav.ids,
                    "add_qty": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        response_large = self.url_open(
            "/website_sale/get_combination_info",
            data=self._make_jsonrpc_payload(
                {
                    "product_template_id": self.product.id,
                    "product_id": self.large.id,
                    "combination": large_ptav.ids,
                    "add_qty": 1,
                }
            ),
            headers={"Content-Type": "application/json"},
        )
        html_small = response_small.json()["result"]["product_documents_html"]
        html_large = response_large.json()["result"]["product_documents_html"]
        self.assertIn("Small Size Chart.pdf", html_small)
        self.assertNotIn("Small Size Chart.pdf", html_large)

    def test_published_variant_document_downloads(self):
        self.authenticate(None, None)
        response = self.url_open(
            f"/shop/{self.product.id}/document/{self.small_document.id}"
        )

        self.assertEqual(response.status_code, 200)
        # The download route itself lives under "/shop/...", so a plain
        # substring check against "/shop" would always match. Check the
        # response wasn't redirected to the bare shop root instead.
        self.assertNotEqual(urlparse(response.url).path, "/shop")

    def test_unpublished_variant_document_redirects_to_shop(self):
        unpublished = self.Document.create(
            {
                "name": "Draft Notes.pdf",
                "datas": FAKE_CONTENT,
                "res_model": "product.product",
                "res_id": self.small.id,
                "shown_on_product_page": False,
            }
        )
        self.authenticate(None, None)
        response = self.url_open(f"/shop/{self.product.id}/document/{unpublished.id}")
        self.assertIn("/shop", response.url)
