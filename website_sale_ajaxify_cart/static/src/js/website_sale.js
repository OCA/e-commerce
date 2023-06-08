odoo.define("website_sale_ajaxify_cart.website_sale", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const wSaleUtils = require("website_sale.utils");

    require("web.dom_ready");

    publicWidget.registry.WebsiteSale.include({
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onClickAdd: function (ev) {
            this.isDynamic = Boolean($(ev.currentTarget).data("is-dynamic"));
            this.pageType = $(ev.currentTarget).data("page-type");
            this.targetEl = $(ev.currentTarget);
            return this._super.apply(this, arguments);
        },
        /**
         * Add custom variant values and attribute values that do not generate variants
         * in the form data and trigger submit.
         *
         * @private
         * @returns {Promise} never resolved
         */
        _submitForm: function () {
            if (!this.isDynamic) {
                return this._super.apply(this, arguments);
            }
            const pageType = this.pageType;
            const params = this.rootProduct;
            params.add_qty = params.quantity;

            params.product_custom_attribute_values = JSON.stringify(
                params.product_custom_attribute_values
            );
            params.no_variant_attribute_values = JSON.stringify(
                params.no_variant_attribute_values
            );

            if (this.isBuyNow) {
                params.express = true;
            }
            this._rpc({
                route: "/shop/cart/ajaxify_update_json",
                params: params,
            }).then((data) => {
                wSaleUtils.updateCartNavBar(data);
                const $navButton = $("header .o_wsale_my_cart").first();
                let el = $();
                if (pageType === "product") {
                    el = $("#o-carousel-product");
                }
                if (pageType === "products") {
                    el = this.targetEl.parents(".o_wsale_product_grid_wrapper");
                }
                wSaleUtils.animateClone($navButton, el, 25, 40);
            });
        },
    });
});
