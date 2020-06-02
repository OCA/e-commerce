# Copyright 2020 Tecnativa - Alexandre Díaz
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import time

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL


class ProductCarouselWebsiteSale(WebsiteSale):
    @http.route(
        ["/website/render_product_carousel"],
        type="json",
        auth="public",
        website=True,
        csrf=False,
        cache=30,
    )
    def render_product_carousel(
        self, domain=False, limit=12, products_per_slide=4, **kwargs
    ):
        # Snippet options only allow a maximium of 24 records
        limit = min(limit, 24)
        _pricelist_context, pricelist = self._get_pricelist_context()
        # Used this way to follow Odoo implementation
        request.context = dict(
            request.context,
            pricelist=pricelist.id,
            partner=request.env.user.partner_id)
        records = request.env["product.template"].search(domain or [], limit=limit)

        records_grouped = []
        record_list = []
        for index, record in enumerate(records, 1):
            record_list.append(record)
            if index % products_per_slide == 0:
                records_grouped.append(record_list)
                record_list = []
        if any(record_list):
            records_grouped.append(record_list)

        template = "website_snippet_carousel_product.s_product_carousel_items"
        return request.website.viewref(template).render(
            {
                "objects": records_grouped,
                "keep": QueryURL("/shop"),
                "pager": request.website.pager(
                    url="/shop", total=limit, scope=7, url_args=kwargs
                ),
                "products_per_slide": products_per_slide,
                "num_slides": len(records_grouped),
                "uniqueId": "pc-%d" % int(time.time() * 1000),
            }
        )
