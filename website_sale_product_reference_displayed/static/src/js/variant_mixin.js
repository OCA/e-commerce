odoo.define("website_sale_product_reference_displayed.variant_mixin", function (
    require
) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.WebsiteSale.include({
        _onChangeCombination: function (ev, $parent, combination) {
            var result = this._super.apply(this, arguments);

            // Dynamically update the variant_reference,
            // and hide it when empty
            var variant_reference = combination.variant_reference;
            var variant_reference_node = $parent
                .parents("#product_details")
                .find(".js_variant_reference_displayed")
                .first();
            if (variant_reference_node) {
                variant_reference_node.text(variant_reference).trigger("change");

                var variant_reference_parent_node = variant_reference_node.parents(
                    ".js_variant_reference_displayed_parent"
                );
                if (variant_reference) {
                    variant_reference_parent_node.removeClass("d-none");
                } else {
                    variant_reference_parent_node.addClass("d-none");
                }
            }
            return result;
        },
    });
});
