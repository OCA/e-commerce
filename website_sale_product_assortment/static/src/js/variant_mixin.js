// Copyright 2021 Tecnativa - Carlos Roca
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("website_sale_product_assortment.VariantMixin", function (require) {
    "use strict";

    var VariantMixin = require("sale.VariantMixin");
    var publicWidget = require("web.public.widget");
    var ajax = require("web.ajax");
    var core = require("web.core");
    var QWeb = core.qweb;
    var xml_load = ajax.loadXML(
        "/website_sale_product_assortment/static/src/xml/website_sale_product_assortment.xml",
        QWeb
    );

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
        xml_load.then(function () {
            $(".oe_website_sale")
                .find("#product_option_block")
                .prepend(
                    QWeb.render(
                        "website_sale_product_assortment.product_availability",
                        combination
                    )
                );
            if (combination.assortment_information) {
                $("#product_detail").after(
                    "<div id='product_full_assortment_description'>" +
                        combination.assortment_information +
                        "</div>"
                );
            }
        });
    };

    publicWidget.registry.WebsiteSale.include({
        /**
         * Adds the stock checking to the regular _onChangeCombination method
         * @override
         */
        _onChangeCombination: function () {
            this._super.apply(this, arguments);
            VariantMixin._onChangeCombinationAssortment.apply(this, arguments);
        },
    });

    return VariantMixin;
});
