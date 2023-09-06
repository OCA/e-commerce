import math

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInfinityScroll(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, ppg=False, search="", **post):
        res = super().shop(
            page=page,
            category=category,
            search=search,
            ppg=self._get_shop_ppg(ppg),
            **post
        )
        return request.render("website_sale.products", res.qcontext)

    def _get_shop_ppg(self, ppg):
        return (
            request.website.shop_ppg + 1
            if request.website.viewref("website_sale_infinite_scroll.scroll_products")
            .sudo()
            .active
            else ppg
        )

    @http.route(
        [
            """/website_sale_infinite_scroll""",
            """/website_sale_infinite_scroll/""" """page/<int:page>""",
            """/website_sale_infinite_scroll/"""
            """category/<model("product.public.category", """
            """"[('website_id', 'in', (False, current_website_id))]")"""
            """:category>""",
            """/website_sale_infinite_scroll/category/"""
            """<model("product.public.category", "[('website_id', 'in', """
            """(False, current_website_id))]"):category>/page/<int:page>""",
        ],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def website_sale_infinite_scroll_get_page(
        self, page=0, category=None, search="", ppg=False, **post
    ):
        if ppg:
            try:
                ppg = int(ppg)
                post["ppg"] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env["website"].get_current_website().shop_ppg or 20
        old_ppg = ppg
        old_page = page
        if page > 0:
            ppg = ppg * page
            page = 1
        res = super().shop(page=page, category=category, search=search, ppg=ppg, **post)
        page_count = int(math.ceil(float(len(res.qcontext["products"])) / old_ppg))
        if old_page > page_count:
            return request.render("website_sale_infinite_scroll.empty_page")
        res.qcontext.update(
            {
                "ppg": old_ppg,
                "page": old_page,
            }
        )
        return request.render(
            "website_sale_infinite_scroll.infinite_products",
            res.qcontext,
        )

    @http.route(
        ["/infinite_scroll_preloader"],
        type="http",
        auth="public",
        website=True,
        multilang=False,
        sitemap=False,
    )
    def get_website_sale_infinite_scroll_preloader(self, **post):
        website = request.website
        response = request.redirect(
            website.image_url(website, "infinite_scroll_preloader"), code=301
        )
        response.headers["Cache-Control"] = (
            "public, max-age=%s" % http.STATIC_CACHE_LONG
        )
        return response
