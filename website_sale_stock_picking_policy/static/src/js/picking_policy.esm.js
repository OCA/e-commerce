// Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";
import {deserializeDate, formatDate} from "@web/core/l10n/dates";

export class WebsiteSalePickingPolicy extends Interaction {
    static selector = "#shop_checkout";

    dynamicContent = {
        '[name="picking_policy"]': {"t-on-change": this.selectPickingPolicy},
    };

    /**
     * Handles picking policy selection and updates the order
     */
    async selectPickingPolicy(ev) {
        const checkedRadio = ev.currentTarget;
        if (checkedRadio.disabled) return;

        const policy = checkedRadio.value;
        const result = await rpc("/shop/update_picking_policy", {
            picking_policy: policy,
        });

        const allDateEls = document.querySelectorAll(".o_picking_policy_date");
        allDateEls.forEach((el) => el.classList.add("d-none"));

        if (policy === "one") {
            const selectedLabel = checkedRadio.closest("label");
            if (!selectedLabel) {
                return;
            }

            const dateEl = selectedLabel.querySelector(".o_picking_policy_date");
            if (dateEl && result && result.expected_date) {
                const dateValueEl = dateEl.querySelector(
                    ".o_picking_policy_date_value"
                );
                if (dateValueEl) {
                    dateValueEl.textContent = formatDate(
                        deserializeDate(result.expected_date)
                    );
                }
                dateEl.classList.remove("d-none");
            }
        }
    }
}

registry
    .category("public.interactions")
    .add("website_sale_stock_picking_policy.picking_policy", WebsiteSalePickingPolicy);
