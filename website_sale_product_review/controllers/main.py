# Copyright 2025 Kencove - Mohamed Alkobrosli
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import http
from odoo.http import request
from odoo.modules import get_module_path


class StarRatingXMLController(http.Controller):
    @http.route(
        "/shop/product_review/portal/<path:file>",
        type="http",
        auth="user",
        website=True,
    )
    def star_rating_xml(self, file, **kwargs):
        content = "<div></div>"
        module_path = get_module_path("website_sale_product_review")
        file_path = os.path.join(module_path, file)
        if os.path.exists(file_path):
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        return request.make_response(
            content,
            headers=[("Content-Type", "text/xml")],
        )

    @http.route(
        '/shop/product_review/<model("product.template"):product_template>/post_review',
        type="json",
        auth="user",
        website=True,
    )
    def post_review(
        self, product_template, access_token=None, rating=None, comment=None, **post
    ):
        if not access_token:
            return {"error": True, "message": "Access token is invalid"}
        if not rating or not comment:
            return {"error": True, "message": "Rating and comment are required."}
        if rating not in [1, 2, 3, 4, 5]:
            return {"error": True, "message": "Invalid rating value."}
        try:
            rating = str(rating)
            request.env["product.review"].sudo().create(
                {
                    "product_id": product_template.id,
                    "rating": rating,
                    "comment": comment.strip(),
                }
            )
            return {"error": False, "message": "Review submitted successfully."}
        except Exception as e:
            return {"error": True, "message": str(e)}

    @http.route(
        '/shop/product_review/<model("product.template"):product_template>/get_reviews',
        type="json",
        auth="public",
        website=True,
    )
    def get_reviews(self, product_template, page=1, rating_filter=None, **post):
        domain = [("product_id", "=", product_template.id)]
        if rating_filter:
            domain.append(("rating", "=", rating_filter))
        limit = 3
        offset = (page - 1) * limit
        reviews = (
            request.env["product.review"]
            .sudo()
            .search(domain, offset=offset, limit=limit, order="create_date desc")
        )
        result = [
            {
                "user": r.partner_id.name,
                "rating": int(r.rating),
                "comment": r.comment,
            }
            for r in reviews
        ]
        total = request.env["product.review"].sudo().search_count(domain)
        return {
            "reviews": result,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
        }
