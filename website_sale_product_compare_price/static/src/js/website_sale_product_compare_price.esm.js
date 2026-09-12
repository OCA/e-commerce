/* Copyright 2026 Domatix
 * License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */

import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

patch(WebsiteSale.prototype, {
    /**
     * Keep the compare price block in sync when the shopper changes the
     * selected variant. The crossed-out reference, the discount badge and the
     * saved amount are re-rendered from the combination returned by the
     * server.
     *
     * @override
     */
    _onChangeCombination(ev, parent, combination) {
        const res = super._onChangeCombination(...arguments);
        const scope = parent?.closest?.(".oe_website_sale") ?? document;
        const blocks = scope.querySelectorAll(".oe_compare_price_block");
        if (!blocks.length) {
            return res;
        }
        const showBlock = Boolean(
            combination.has_compare_price || combination.compare_save_text
        );
        for (const block of blocks) {
            block.classList.toggle("d-none", !showBlock);
            this._updateComparePriceBlock(block, combination);
        }
        // The native template-level "Compare to Price" strikethrough is hidden
        // while the variant reference price is displayed by this module.
        const nativeCompare = scope.querySelector(".oe_compare_list_price");
        if (nativeCompare) {
            nativeCompare.classList.toggle(
                "d-none",
                Boolean(combination.has_compare_price)
            );
        }
        return res;
    },

    _updateComparePriceBlock(block, combination) {
        const del = block.querySelector(".oe_compare_price_del");
        const delValue = del?.querySelector(".oe_compare_price_value");
        const badge = block.querySelector(".oe_compare_badge");
        const save = block.querySelector(".oe_compare_save");
        const showDel = Boolean(combination.has_compare_price);
        if (del) {
            del.classList.toggle("d-none", !showDel);
            if (delValue) {
                delValue.textContent = showDel
                    ? combination.compare_price_formatted || ""
                    : "";
            }
        }
        if (badge) {
            badge.classList.toggle("d-none", !combination.compare_badge_text);
            badge.textContent = combination.compare_badge_text || "";
        }
        if (save) {
            save.classList.toggle("d-none", !combination.compare_save_text);
            save.textContent = combination.compare_save_text || "";
        }
    },
});
