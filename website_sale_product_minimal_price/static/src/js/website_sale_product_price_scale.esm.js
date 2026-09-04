/* Copyright 2021 Carlos Roca
 * Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {formatCurrency} from "@web/core/currency";
import {patch} from "@web/core/utils/patch";
import {renderToString} from "@web/core/utils/render";

patch(WebsiteSale.prototype, {
    _onChangeCombination(ev, parent, combination) {
        super._onChangeCombination(...arguments);
        if (!this.isWebsite || combination.product_id === false) {
            return;
        }

        const unitPrices = combination.minimal_price_scale || [];
        const visiblePrices = unitPrices.filter((line) => line.price !== 0);
        const uomName = combination.uom_name;
        const form =
            parent?.querySelector("form") || document.querySelector(".js_product form");
        if (!form) {
            return;
        }

        form.querySelectorAll(".o_wsmp_temp").forEach((el) => el.remove());
        if (!visiblePrices.length) {
            return;
        }

        const anchor =
            form.querySelector("#o_wsale_cta_wrapper") || form.lastElementChild;
        anchor.insertAdjacentHTML("afterend", '<div class="o_wsmp_temp"></div>');
        const container = anchor.nextElementSibling;

        container.insertAdjacentHTML("beforeend", "<hr/>");
        container.insertAdjacentHTML(
            "beforeend",
            renderToString("website_sale_product_minimal_price.title", {uom: uomName})
        );

        const limitCol = 4;
        let rowEl = null;
        for (const [index, line] of visiblePrices.entries()) {
            if (index % limitCol === 0) {
                rowEl = document.createElement("div");
                rowEl.className = "row";
                container.append(rowEl);
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

        const rows = container.querySelectorAll(".row");
        rows.forEach((row, index) => {
            row.classList.toggle("border-bottom", index < rows.length - 1);
        });
    },
});
