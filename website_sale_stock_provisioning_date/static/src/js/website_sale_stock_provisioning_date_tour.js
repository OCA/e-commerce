/* Copyright 2020 Tecnativa - Ernesto Tejeda
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
odoo.define("website_sale_stock_provisioning_date.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");

    var steps = [
        {
            content: "search provisioning date",
            trigger: 'form input[name="search"]',
            run: "text provisioning date",
        },
        {
            content: "search provisioning date",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
        },
        {
            content: "click on product test",
            trigger: '.oe_product_cart a:contains("provisioning date")',
        },
        {
            trigger: "a#add_to_cart",
            extra_trigger: ".availability_messages:has(span:contains('Next provisioning date:'))",
        },
    ];
    tour.register("website_sale_stock_provisioning_date",
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
