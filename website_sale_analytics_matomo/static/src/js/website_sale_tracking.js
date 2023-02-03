odoo.define("website_sale_analytics_matomo.matomo_analytics", function (require) {
    "use strict";

    const websiteSaleTracking = require("website_sale.tracking");

    websiteSaleTracking.include({
        /**
         * @override
         */
        start: function () {
            // Track purchase event
            const $confirmation = this.$("div.oe_website_sale_tx_status");
            if ($confirmation.length) {
                const json = $confirmation.data("order-tracking-info");
                const websiteMA =
                    window._paq ||
                    function () {
                        // Do nothing.
                    };
                websiteMA.push([
                    "trackEcommerceOrder",
                    json.order_name, // (Required) orderId
                    json.value, // (Required) grandTotal (revenue)
                    json.subtotal, // (Optional) subTotal
                    json.tax, // (optional) tax
                    json.shipping || false, // (optional) shipping
                    false, // (optional) discount
                ]);
            }

            return this._super.apply(this, arguments);
        },

        /**
         * @private
         */
        _vpv: function (page) {
            // Track virtual page view
            const websiteMA =
                window._paq ||
                function () {
                    // Do nothing.
                };
            websiteMA.push(["setDocumentTitle", page]);
            websiteMA.push(["trackPageView"]);

            return this._super.apply(this, arguments);
        },

        /**
         * @private
         */
        _onViewItem(event, productTrackingInfo) {
            // Track viewing of a product
            const websiteMA =
                window._paq ||
                function () {
                    // Do nothing.
                };
            websiteMA.push([
                "setEcommerceView",
                productTrackingInfo.item_id, // (Required) productSKU
                productTrackingInfo.item_name, // (Optional) productName
                productTrackingInfo.item_category, // (Optional) categoryName
                productTrackingInfo.price, // (Optional) price
            ]);

            // You must also call trackPageView when tracking a product view
            websiteMA.push(["trackPageView"]);

            return this._super.apply(this, arguments);
        },

        /**
         * @private
         */
        _onAddToCart(event, ...productsTrackingInfo) {
            // Adding a Product to the order
            const websiteMA =
                window._paq ||
                function () {
                    // Do nothing.
                };
            websiteMA.push([
                "addEcommerceItem",
                productsTrackingInfo[0].item_id, // (required) SKU: Product unique identifier
                productsTrackingInfo[0].item_name, // (Optional) productName
                false, // (optional) Product category
                productsTrackingInfo[0].price, // (Recommended) Product Price
                productsTrackingInfo[0].quantity, // (Optional - Defaults to 1)
            ]);

            // Pass the Cart's Total Value as a numeric parameter
            const value = productsTrackingInfo.reduce(
                (acc, val) => acc + val.price * val.quantity,
                0
            );
            websiteMA.push(["trackEcommerceCartUpdate", value]);

            return this._super.apply(this, arguments);
        },
    });
});
