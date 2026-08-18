/* Copyright 2026 Camptocamp SA
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {patch} from "@web/core/utils/patch";
import {WebsiteSale} from "@website_sale/interactions/website_sale";

patch(WebsiteSale.prototype, {
    _onChangeCombination(ev, parent, combination) {
        const res = super._onChangeCombination(...arguments);
        const extraFields = combination.variant_extra_fields;
        if (!extraFields) {
            return res;
        }
        const container = document.querySelector("#o_wsale_extra_fields");
        if (!container) {
            return res;
        }
        for (const [name, value] of Object.entries(extraFields)) {
            const fieldEl = container.querySelector(`[data-extra-field="${name}"]`);
            const valueEl = fieldEl?.querySelector(".o_wsale_extra_field_value");
            if (!valueEl) {
                continue;
            }
            // Values are rendered server side by the ir.qweb.field converters.
            valueEl.innerHTML = value;
            fieldEl.classList.toggle("d-none", !value);
        }
        return res;
    },
});
