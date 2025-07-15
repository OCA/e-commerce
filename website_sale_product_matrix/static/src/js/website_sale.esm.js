/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import wUtils from "@website/js/utils";

// If next dependency is not declared publicWidget.registry.WebsiteSale will be
// undefined
import "@website_sale/js/website_sale";

// TODO: Add logic to improve UX
publicWidget.registry.WebsiteSale.include({
    events: Object.assign({}, publicWidget.registry.WebsiteSale.prototype.events, {
        "click .o_we_order_matrix": "addToCartFromMatrix",
    }),
    /**
     * Avoid stay on page when the matrix is loaded so we refresh the page every time
     * @override
     */
    async start() {
        await this._super.apply(this, arguments);
        const html = document.documentElement;
        if (Object.hasOwn(html.dataset, "productAddMode")) {
            this.stayOnPageOption =
                this.stayOnPageOption && html.dataset.productAddMode !== "matrix";
        }
    },
    /**
     * Overridable method to add stuff to the grid
     * @param {Number} product_template_id
     * @param {HTMLFormElement} $form
     * @returns {Object}
     */
    _parseGridChanges(product_template_id, $form) {
        const inputs = $form.getElementsByClassName("o_matrix_input");
        const changes = Array.from(inputs).map((input) => {
            return {
                qty: parseInt(input.value, 10) || 0,
                ptav_ids: JSON.parse(input.dataset.ptav_ids),
            };
        });
        return {
            product_template_id: product_template_id,
            changes: changes,
        };
    },
    /**
     * Parse the grid with the changes to apply into the order
     * @param {Event} ev
     * @returns {Promise<Object>}
     */
    addToCartFromMatrix(ev) {
        const $form = ev.currentTarget.closest("form");
        const params = {
            product_template_id: parseInt($form.dataset.product_template_id, 10),
        };
        const grid = this._parseGridChanges(params.product_template_id, $form);
        params.grid = JSON.stringify(grid);
        return wUtils.sendRequest("/shop/cart/update_from_matrix", params);
    },
});
