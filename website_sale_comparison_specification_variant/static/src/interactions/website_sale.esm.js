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
        this._onChangeCombinationSpecsAccordion(...args);
    },

    /**
     * Refreshes the "Specifications" table so that attribute values
     * excluded for the newly selected combination stop being displayed.
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

    /**
     * Same as `_onChangeCombinationSpecsTable`, but for the "Specifications"
     * accordion item: each category's body is refreshed individually,
     * leaving the `accordion-collapse`/`accordion-header` wrappers
     * untouched so the accordion's open/collapsed state survives the
     * refresh.
     *
     * @param {MouseEvent} ev
     * @param {Element} parent
     * @param {Array} combination
     */
    _onChangeCombinationSpecsAccordion(ev, parent, combination) {
        if (combination.specs_accordion_html === undefined) {
            return;
        }
        const categoryEls = new DOMParser()
            .parseFromString(combination.specs_accordion_html, "text/html")
            .querySelectorAll("[data-category-index]");
        categoryEls.forEach((categoryEl) => {
            const accordionBodyEl = document.querySelector(
                `#category_accordion_${categoryEl.dataset.categoryIndex} .accordion-body`
            );
            if (accordionBodyEl) {
                setElementContent(accordionBodyEl, markup(categoryEl.innerHTML));
            }
        });
    },
});
