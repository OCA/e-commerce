/** @odoo-module */
/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {WebsiteSale} from "@website_sale/js/website_sale";
import {formatCurrency} from "@web/core/currency";
import {renderToString} from "@web/core/utils/render";

WebsiteSale.include({
    /**
     * @override
     * Render the price scale of the product
     * based on the selected combination and current pricelist .
     */
    _onChangeCombination: function (ev, $parent, combination) {
        const res = this._super(...arguments);
        if (!this.isWebsite) {
            return res;
        }
        const unit_prices = combination.minimal_price_scale;
        const uom_name = combination.uom_name;
        $(".temporal").remove();
        if (unit_prices.length <= 0) {
            return res;
        }
        const $form = $('form[action*="/shop/cart/update"]');
        $form.append('<hr class="temporal"/>');
        $form.append(
            renderToString("website_sale_product_minimal_price.title", {uom: uom_name})
        );
        // We define a limit of displayed columns as 4
        const limit_col = 4;
        let $div; // eslint-disable-line init-declarations
        for (const i in unit_prices) {
            if (unit_prices[i].price === 0) {
                continue;
            }
            if (i % limit_col === 0) {
                const id = i / limit_col;
                $form.append('<div id="row_' + id + '" class="row temporal"></div>');
                $div = $("#row_" + id);
            }
            let monetary_u = formatCurrency(
                unit_prices[i].price,
                unit_prices[i].currency_id
            );
            monetary_u = monetary_u.replace("&nbsp;", " ");
            $div.append(
                renderToString("website_sale_product_minimal_price.pricelist", {
                    quantity: unit_prices[i].min_qty,
                    price: monetary_u,
                })
            );
        }
        $div = $('div[id*="row_"]');
        for (let i = 0; i < $div.length - 1; i++) {
            $($div[i]).addClass("border-bottom");
        }
        return res;
    },
});
