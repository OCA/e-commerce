/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

 odoo.define("website_sale_require_legal.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "a:contains('iPod')",
        },
        {
            trigger: "#add_to_cart",
        },
        {
            trigger: ".btn-primary:contains('Process Checkout')",
        },
        {
            trigger: "a.js_edit_address:first",
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
        {
            trigger: ".form-group.has-error #accepted_legal_terms",
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
        {
            trigger: "form[action='/shop/address'] a",
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
        {
            trigger: ".form-group.has-error #accepted_legal_terms",
        },
        {
            trigger: ".btn-primary:contains('Next')",
        },
    ];

    tour.register(
        "website_sale_require_legal",
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
