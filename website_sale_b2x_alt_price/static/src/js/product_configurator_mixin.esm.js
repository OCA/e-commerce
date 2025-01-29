/* Copyright 2020 Jairo Llopis - Tecnativa
 * Copyright 2022 Carlos Roca - Tecnativa
 * Copyright 2024 Carlos Lopez - Tecnativa
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {WebsiteSale} from "@website_sale/js/website_sale";

WebsiteSale.include({
    /**
     * Add alt price onchange to the regular _onChangeCombination method.
     *
     * @override
     */
    _onChangeCombination: function (ev, $parent, combination) {
        // Write new alt prices
        $parent
            .find(".js_alt_price .oe_currency_value")
            .text(this._priceToStr(combination.alt_price));
        $parent
            .find(".js_alt_list_price")
            .toggleClass("d-none", !combination.has_discounted_price)
            .find(".oe_currency_value")
            .text(this._priceToStr(combination.alt_list_price));
        return this._super(...arguments);
    },
});
