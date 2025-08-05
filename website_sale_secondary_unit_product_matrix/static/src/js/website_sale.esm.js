/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

// If next dependency is not declared publicWidget.registry.WebsiteSale will be
// undefined
import "@website_sale/js/website_sale";

// TODO: Add logic to improve UX
publicWidget.registry.WebsiteSale.include({
    /**
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
            (selected_secondary_unit && parseInt(selected_secondary_unit)) || false;
        return grid;
    },
});
