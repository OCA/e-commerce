import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {markup} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {setElementContent} from "@web/core/utils/html";

patch(WebsiteSale.prototype, {
    /**
     * Adds the specs table refresh to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination(...args) {
        super._onChangeCombination(...args);
        this._onChangeCombinationSpecsTable(...args);
    },

    /**
     * Refreshes the "Specifications" table so that non-variant-defining
     * attribute values excluded for the newly selected combination stop
     * being displayed.
     *
     * @param {MouseEvent} ev
     * @param {Element} parent
     * @param {Array} combination
     */
    _onChangeCombinationSpecsTable(ev, parent, combination) {
        if (combination.specs_table_html === undefined) {
            return;
        }
        const specsTableEl = document.querySelector("#product_specifications");
        if (specsTableEl) {
            setElementContent(specsTableEl, markup(combination.specs_table_html));
        }
    },
});
