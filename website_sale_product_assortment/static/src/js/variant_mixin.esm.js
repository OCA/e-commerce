// Copyright 2021 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {markup} from "@odoo/owl";
import publicWidget from "@web/legacy/js/public/public_widget";
import {renderToElement} from "@web/core/utils/render";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import "@website_sale/js/website_sale";

VariantMixin._onChangeCombinationAssortment = function (ev, $parent, combination) {
    let product_id = 0;
    if ($parent.find("input.product_id:checked").length) {
        product_id = $parent.find("input.product_id:checked").val();
    } else {
        product_id = $parent.find(".product_id").val();
    }
    const isMainProduct =
        combination.product_id &&
        ($parent.is(".js_main_product") || $parent.is(".main_product")) &&
        combination.product_id === parseInt(product_id);
    if (!this.isWebsite || !isMainProduct) {
        return;
    }
    $(".oe_website_sale")
        .find("#message_unavailable_" + combination.product_template_id)
        .remove();
    $("#product_full_assortment_description").remove();
    if (!combination.product_avoid_purchase) {
        return;
    }
    $parent.find("#add_to_cart").addClass("disabled");
    $parent.find("#buy_now").addClass("disabled");
    const message = renderToElement(
        "website_sale_product_assortment.product_availability",
        combination
    );

    $(".oe_website_sale").find("#product_option_block").prepend(message);

    if (combination.assortment_information) {
        const assortment_information = renderToElement(
            "website_sale_product_assortment.assortment_information",
            {
                assortment_information: markup(combination.assortment_information),
            }
        );
        $("#product_detail").after(assortment_information);
    }
};

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function () {
        this._super.apply(this, arguments);
        VariantMixin._onChangeCombinationAssortment.apply(this, arguments);
    },
});

export default VariantMixin;
