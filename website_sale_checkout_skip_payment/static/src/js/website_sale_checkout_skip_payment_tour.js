/* Copyright 2019 Sergio Teruel
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_checkout_skip_payment.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            trigger: "a:contains('Customizable Desk')",
        },
        {
            trigger: "a:contains('Add to Cart')",
        },
        {
            trigger: ".btn-primary:contains('Process Checkout')",
        },
        {
            trigger: ".btn:contains('Confirm Order')",
        },
        {
            trigger: "a[href='/shop']",
            extra_trigger: "h2:contains('Thank you for your order')",
        },
    ];
    tour.register("website_sale_checkout_skip_payment",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        steps
    );
    return {
        steps: steps,
    };
});
