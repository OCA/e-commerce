/** @odoo-module **/

odoo.define(
    "website_sale_charge_payment_fee.tour",
    ["web_tour.tour", "@website/js/tours/tour_utils"],
    function (require) {
        const tour = require("web_tour.tour");
        const wTourUtils = require("@website/js/tours/tour_utils").default;

        const steps = [
            ...wTourUtils.addToCart({productName: "Product Test", search: true}),

            wTourUtils.goToCart(),

            wTourUtils.goToCheckout(),

            ...wTourUtils.payWithDemo(),
        ];

        tour.register("website_sale_order_payment_fee_tour", steps, {
            test: true,
            url: "/shop",
        });
    }
);
