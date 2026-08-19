# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.http import request, route

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleProductDocumentVariant(WebsiteSale):
    @route(
        '/shop/<model("product.template"):product_template>/document/<int:document_id>',
        type="http",
        auth="public",
        website=True,
        sitemap=False,
        readonly=True,
    )
    def product_document(self, product_template, document_id):
        # Full override: the base method only accepts template documents
        # (`res_model == 'product.template'`); this also accepts a
        # document scoped to one of the template's own variants.
        product_template.check_access("read")

        document = request.env["product.document"].browse(document_id).sudo().exists()
        if not document or not document.active or not document.shown_on_product_page:
            return request.redirect(self._get_shop_path())

        is_template_document = (
            document.res_model == "product.template"
            and document.res_id == product_template.id
        )
        is_variant_document = (
            document.res_model == "product.product"
            and document.res_id in product_template.product_variant_ids.ids
        )
        if not (is_template_document or is_variant_document):
            return request.redirect(self._get_shop_path())

        return (
            request.env["ir.binary"]
            ._get_stream_from(
                document.ir_attachment_id,
            )
            .get_response(as_attachment=True)
        )
