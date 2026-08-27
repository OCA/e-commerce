/* Copyright 2024 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html). */

// If next dependency is not declared, publicWidget.registry.WebsiteSaleProductMatrix
// will be undefined
import "@website_sale_product_matrix/js/website_sale.esm";
import publicWidget from "@web/legacy/js/public/public_widget";

// TODO: Add logic to improve UX
publicWidget.registry.WebsiteSaleProductMatrix.include({
    /**
     * Send the unit selected for the whole matrix along with the grid changes.
     *
     * @override
     */
    _parseGridChanges(product_template_id, $form) {
        const grid = this._super.apply(this, arguments);
        const secondary_unit_select = $form.getElementsByClassName(
            "o_matrix_secondary_unit"
        );
        if (!secondary_unit_select.length) {
            return grid;
        }
        // Reduce to get the selected option value
        const selected_secondary_unit = Array.from(secondary_unit_select).reduce(
            (_, select) => select.value,
            null
        );
        grid.secondary_unit =
            (selected_secondary_unit && parseInt(selected_secondary_unit, 10)) || false;
        return grid;
    },
});
