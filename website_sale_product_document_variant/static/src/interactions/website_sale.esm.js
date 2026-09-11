import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {markup} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {setElementContent} from "@web/core/utils/html";

patch(WebsiteSale.prototype, {
    /**
     * Adds the documents section refresh to the regular
     * _onChangeCombination method
     * @override
     */
    _onChangeCombination(...args) {
        super._onChangeCombination(...args);
        this._onChangeCombinationDocuments(...args);
    },

    /**
     * Refreshes the "Documents" section to match the newly selected
     * variant, hiding it entirely when that variant (combined with the
     * template) has nothing published.
     *
     * @param {MouseEvent} ev
     * @param {Element} parent
     * @param {Object} combination
     */
    _onChangeCombinationDocuments(ev, parent, combination) {
        if (combination.product_documents_html === undefined) {
            return;
        }
        const documentsEl = document.querySelector("#product_documents");
        if (!documentsEl) {
            return;
        }
        setElementContent(documentsEl, markup(combination.product_documents_html));
        documentsEl.classList.toggle(
            "d-none",
            !combination.product_documents_html.trim()
        );
    },
});
