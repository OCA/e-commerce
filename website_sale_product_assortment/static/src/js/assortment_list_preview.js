/** @odoo-module **/
// Copyright 2021 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {jsonrpc} from "@web/core/network/rpc_service";
import publicWidget from "@web/legacy/js/public/public_widget";
import {renderToFragment} from "@web/core/utils/render";

export const WebsiteSaleProductAssortment = publicWidget.Widget.extend({
    selector: "#products_grid",

    start: function () {
        this._super.apply(this, arguments);
        this.render_assortments();
    },

    render_assortments: function () {
        const $products = $(".o_wsale_product_grid_wrapper");
        const product_dic = {};
        $products.each(function () {
            product_dic[this.querySelector("a img").src.split("/")[6]] = this;
        });
        const product_ids = Object.keys(product_dic).map(Number);
        return jsonrpc("/sale/get_info_assortment_preview", {
            product_template_ids: product_ids,
        }).then((product_values) => {
            for (const product of product_values) {
                this.render_product_assortment(product_dic[product.id], product);
            }
        });
    },

    render_product_assortment: function (product_info, product) {
        $(product_info)
            .find(".product_price")
            .append(
                renderToFragment(
                    "website_sale_product_assortment.product_availability",
                    {
                        message_unavailable: product.message_unavailable,
                        product_template_id: product.id,
                    }
                )
            );
        $(product_info).find(".fa-shopping-cart").parent().addClass("disabled");
    },
});

publicWidget.registry.WebsiteSaleProductAssortment = WebsiteSaleProductAssortment;
