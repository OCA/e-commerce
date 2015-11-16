# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, http


class ProductLegalTerms(http.Controller):
    @http.route(
        "/website_sale_product_legal/<model('product.template'):product>",
        type="http", auth="public", website=True)
    def by_product(self, product):
        """Get legal terms by product."""
        if product.legal_term_ids:
            return http.request.website.render(
                "website_sale_product_legal.legal_terms",
                self._render_values(product))
        else:
            raise http.request.NotFound()

    def _render_values(self, product):
        """Values to render the legal_terms template."""
        return {
            "additional_title":
                _("Legal terms to buy %s") % product.name_get()[0][1],
            "legal_terms": product.legal_term_ids,
            "product": product,
        }
