/* Copyright 2025 Tecnativa - Pilar Vargas
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_acquirer_confirm_order.tour", function (require) {
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
            content: "Select `Wire Transfer` payment method",
            trigger: '#payment_method label:contains("Wire Transfer")',
        },
        {
            trigger: "#o_payment_form_pay:contains('Pay Now')",
            extra_trigger: "#shipping_and_billing",
        },
        {
            trigger: "h3:contains('Payment Information')",
        },
    ];
    tour.register(
        "website_sale_acquirer_confirm_order",
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
