/* Copyright 2025 Carlos Lopez - Tecnativa
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

/** @odoo-module **/

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_vat_required_tour", {
    test: true,
    url: "/shop",
    steps: () => [
        {
            content: "Open product page",
            trigger: "a:contains('Test Product Vat Required')",
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Add product to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        tourUtils.goToCart({quantity: 1}),
        tourUtils.goToCheckout(),
        {
            content: "Set country",
            trigger: 'select[name="country_id"]',
            run: "selectByLabel Afghanistan",
        },
        {
            content: "Set name",
            trigger: 'input[name="name"]',
            run: "edit Mr. Test",
        },
        {
            content: "Set email",
            trigger: 'input[name="email"]',
            run: "edit test@test.com",
        },
        {
            content: "Set phone",
            trigger: 'input[name="phone"]',
            run: "edit 11111111",
        },
        {
            content: "Set street",
            trigger: 'input[name="street"]',
            run: "edit Test Street",
        },
        {
            content: "Set city",
            trigger: 'input[name="city"]',
            run: "edit Test City",
        },
        {
            content: "Set ZIP",
            trigger: 'input[name="zip"]',
            run: "edit 10000",
        },
        {
            content: "Submit address",
            trigger: 'a[name="website_sale_main_button"]',
            run: "click",
        },
        {
            content: "VAT must be required",
            trigger: 'input[name="vat"].is-invalid',
        },
        {
            content: "Fill VAT",
            trigger: 'input[name="vat"]',
            run: "edit VAT123",
        },
        {
            content: "Submit again",
            trigger: 'a[name="website_sale_main_button"]',
            run: "click",
            expectUnloadPage: true,
        },
    ],
});
