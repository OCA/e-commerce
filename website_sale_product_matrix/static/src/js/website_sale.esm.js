import publicWidget from "@web/legacy/js/public/public_widget";
import wUtils from "@website/js/utils";

publicWidget.registry.WebsiteSaleProductMatrix = publicWidget.Widget.extend({
    selector: "#product_detail",
    events: {
        "click .o_we_order_matrix": "addToCartFromMatrix",
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
