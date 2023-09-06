/* Copyright 2020 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_invoice_address.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a:contains('Large Cabinet')",
        },
        {
            trigger: "a:contains('Add to Cart')",
        },
        {
            trigger: ".btn-primary:contains('Process Checkout')",
        },
    ];
    tour.register(
        "website_sale_invoice_address_tour",
        {
            url: "/shop",
            test: true,
        },
        steps
    );
    return {
        steps: steps,
    };
});
