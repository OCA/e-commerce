# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.sale.controllers.variant import VariantController


class WebsiteSaleVariantController(VariantController):
    @http.route(
        ["/sale/get_combination_info_minimal_price"],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def get_combination_info_minimal_price(self, product_template_ids, **kw):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        res = []
        templates = request.env["product.template"].sudo().browse(product_template_ids)
        pricelist = request.env["website"].get_current_website().get_current_pricelist()
        for template in templates.filtered(lambda t: t.is_published):
            product_id, add_qty, has_distinct_price = template._get_cheapest_info(
                pricelist
            )
            combination = template._get_combination_info(
                product_id=product_id, add_qty=add_qty, pricelist=pricelist
            )
            res.append(
                {
                    "id": template.id,
                    "price": combination.get("price"),
                    "distinct_prices": has_distinct_price,
                    "currency": {
                        "position": template.currency_id.position,
                        "symbol": template.currency_id.symbol,
                    },
                }
            )
        return res

    @http.route(
        ["/sale/get_combination_info_pricelist_atributes"],
        type="json",
        auth="public",
        website=True,
    )
    def get_combination_info_pricelist_atributes(self, product_id, **kwargs):
        """Special route to use website logic in get_combination_info override.
        This route is called in JS by appending _website to the base route.
        """
        product = request.env["product.product"].browse(product_id)
        pricelist = request.env["website"].get_current_website().get_current_pricelist()
        # Getting all min_quantity of the current product to compute the possible
        # price scale.
        qty_list = request.env["product.pricelist.item"].search(
            [
                "|",
                ("product_id", "=", product.id),
                "|",
                ("product_tmpl_id", "=", product.product_tmpl_id.id),
                (
                    "categ_id",
                    "in",
                    list(map(int, product.categ_id.parent_path.split("/")[0:-1])),
                ),
                ("min_quantity", ">", 0),
            ]
        )
        qty_list = sorted(set(qty_list.mapped("min_quantity")))
        res = []
        ctx = dict(request.env.context, pricelist=pricelist.id, quantity=0)
        last_price = product.with_context(ctx).price
        for min_qty in qty_list:
            ctx["quantity"] = min_qty
            new_price = product.with_context(ctx).price
            if new_price != last_price:
                res.append(
                    {
                        "min_qty": min_qty,
                        "price": new_price,
                        "currency": {
                            "position": product.currency_id.position,
                            "symbol": product.currency_id.symbol,
                        },
                    }
                )
                last_price = new_price
        return (res, product.uom_name)
