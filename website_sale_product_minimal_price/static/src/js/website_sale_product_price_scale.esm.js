/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import VariantMixin from "@website_sale/js/variant_mixin";
import {formatCurrency} from "@web/core/currency";
import {renderToString} from "@web/core/utils/render";

const oldOnChangeCombination = VariantMixin._onChangeCombination;

VariantMixin._onChangeCombination = function (ev, parent, combination) {
    oldOnChangeCombination.apply(this, arguments);
    if (!this.isWebsite || combination.product_id === false) {
        return;
    }

    const unitPrices = combination.minimal_price_scale || [];
    const visiblePrices = unitPrices.filter((line) => line.price !== 0);
    const uomName = combination.uom_name;
    const form =
        parent?.closest('form[action*="/shop/cart/update"]') ||
        document.querySelector('form[action*="/shop/cart/update"]');
    if (!form) {
        return;
    }

    form.querySelectorAll(".o_wsmp_temp").forEach((el) => el.remove());
    if (!visiblePrices.length) {
        return;
    }

    form.insertAdjacentHTML("beforeend", '<hr class="o_wsmp_temp"/>');
    form.insertAdjacentHTML(
        "beforeend",
        renderToString("website_sale_product_minimal_price.title", {uom: uomName})
    );

    const limitCol = 4;
    let rowEl = null;
    for (const [index, line] of visiblePrices.entries()) {
        if (index % limitCol === 0) {
            rowEl = document.createElement("div");
            rowEl.className = "row o_wsmp_temp";
            form.append(rowEl);
        }
        let unitPrice = formatCurrency(line.price, line.currency_id);
        unitPrice = unitPrice.replace("&nbsp;", " ");
        rowEl.insertAdjacentHTML(
            "beforeend",
            renderToString("website_sale_product_minimal_price.pricelist", {
                quantity: line.min_qty,
                price: unitPrice,
            })
        );
    }

    const rows = form.querySelectorAll(".row.o_wsmp_temp");
    rows.forEach((row, index) => {
        row.classList.toggle("border-bottom", index < rows.length - 1);
    });
};
