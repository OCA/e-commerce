/* Copyright 2020 Jairo Llopis - Tecnativa
 * Copyright 2022 Carlos Roca - Tecnativa
 * Copyright 2024 Carlos Lopez - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

patch(WebsiteSale.prototype, {
    /**
     * Add alt price onchange to the regular _onChangeCombination method.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        // Write new alt prices only when the corresponding DOM nodes exist.
        const altPriceValue = parent.querySelector(".js_alt_price .oe_currency_value");
        if (altPriceValue) {
            altPriceValue.textContent = this._priceToStr(combination.alt_price);
        }
        const altListPrice = parent.querySelector(".js_alt_list_price");
        if (altListPrice) {
            altListPrice.classList.toggle("d-none", !combination.has_discounted_price);
        }
        const altListPriceValue = parent.querySelector(
            ".js_alt_list_price .oe_currency_value"
        );
        if (altListPriceValue) {
            altListPriceValue.textContent = this._priceToStr(
                combination.alt_list_price
            );
        }
        return super._onChangeCombination(...arguments);
    },
});
