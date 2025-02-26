/* Copyright 2025 Carlos Lopez - Tecnativa
  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {registry} from "@web/core/registry";
registry.category("web_tour.tours").add("website_sale_vat_required_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            trigger: "a:contains('Test Product Vat Required')",
            run: "click",
        },
        {
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            trigger: "sup.my_cart_quantity:contains('1')",
            run: "click",
        },
        {
            trigger: "a[href='/shop/cart']",
            run: "click",
        },
        {
            trigger: "a:contains('Checkout')",
            run: "click",
        },
        {
            content: "Next",
            trigger: ".btn-primary:contains('Continue checkout')",
            run: "click",
        },
        {
            content: "Set name",
            trigger: "#o_name",
            run: "edit Mr. Test",
        },
        {
            content: "Set email",
            trigger: "#o_email",
            run: "edit test@test.com",
        },
        {
            content: "Set phone",
            trigger: "#o_phone",
            run: "edit 11111111",
        },
        {
            content: "Set street",
            trigger: "#o_street",
            run: "edit Test Street",
        },
        {
            content: "Set city",
            trigger: "#o_city",
            run: "edit Test City",
        },
        {
            content: "Next",
            trigger: ".btn-primary:contains('Continue checkout')",
        },
        {
            content: "Check there is a warning for required field.",
            trigger: ":invalid",
        },
        {
            content: "Set vat",
            trigger: "input[name='vat']",
            run: "edit VAT",
        },
        {
            content: "Next",
            trigger: ".btn-primary:contains('Continue checkout')",
        },
    ],
});
