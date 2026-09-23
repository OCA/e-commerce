/* Copyright 2026 Tecnativa - Carlos Roca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, markup, onMounted, useRef} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class ProductMatrixDialog extends Component {
    static components = {Dialog};
    static template = "website_sale_product_matrix.ProductMatrixDialog";
    static props = {
        // The matrix, rendered as in the product page.
        html: String,
        rows: Array,
        save: Function,
        close: Function,
    };

    setup() {
        this.matrixRef = useRef("matrix");
        this.matrixHtml = markup(this.props.html);
        this.cellsByPtavIds = new Map(
            this.props.rows
                .flat()
                .filter((cell) => cell.ptav_ids)
                .map((cell) => [String(cell.ptav_ids), cell])
        );
        onMounted(() => {
            for (const input of this.matrixRef.el.querySelectorAll(".o_matrix_input")) {
                input.value = this._getInputCell(input)?.qty || 0;
            }
        });
    }

    /**
     * @param {HTMLInputElement} input - A quantity input of the matrix.
     * @returns {Object|undefined} The matrix cell of the variant.
     */
    _getInputCell(input) {
        return this.cellsByPtavIds.get(String(JSON.parse(input.dataset.ptav_ids)));
    }

    /**
     * The buttons are handled by `website_sale` in the product page, which
     * doesn't reach the dialog.
     *
     * @param {Event} ev
     */
    onClickQuantityButton(ev) {
        const button = ev.target.closest("a.js_add_cart_json");
        if (!button) {
            return;
        }
        ev.preventDefault();
        const input = button.closest(".input-group").querySelector(".o_matrix_input");
        input.value =
            (parseInt(input.value, 10) || 0) + (button.name === "remove_one" ? -1 : 1);
        input.dispatchEvent(new Event("change", {bubbles: true}));
    }

    /**
     * @param {Event} ev
     */
    onChangeQuantity(ev) {
        const input = ev.target.closest(".o_matrix_input");
        const cell = input && this._getInputCell(input);
        if (!cell) {
            return;
        }
        cell.qty = Math.max(parseInt(input.value, 10) || 0, 0);
        input.value = cell.qty;
    }

    /**
     * Report the variants with a quantity to the product configurator.
     */
    onConfirm() {
        this.props.save(
            [...this.cellsByPtavIds.values()]
                .filter((cell) => cell.qty > 0)
                .map(({ptav_ids, qty, combination_name, unit_price}) => ({
                    ptav_ids,
                    qty,
                    name: combination_name,
                    unit_price,
                }))
        );
        this.props.close();
    }
}
