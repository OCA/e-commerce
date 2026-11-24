/** @odoo-module **/

import * as tourUtils from "@website_sale/js/tours/tour_utils";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_address_format_state", {
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({
            productName: "Address Format Test Product",
            expectUnloadPage: true,
        }),
        tourUtils.goToCart(),
        tourUtils.goToCheckout(),
        {
            content: "Select a country whose online format uses state_code",
            trigger: "select[name='country_id']",
            run: "selectByLabel Japan",
        },
        {
            content: "Pick a state",
            trigger: "select[name='state_id']:has(option:contains(Tokyo))",
            run: "selectByLabel Tokyo",
        },
        {
            content: "Select a country without states",
            trigger: "select[name='country_id']",
            run: "selectByLabel Afghanistan",
        },
        {
            content: "The previous country's states are cleared",
            trigger:
                "select[name='state_id']:not(:visible):not(:has(option:nth-child(2)))",
        },
        {
            content: "Select a country whose core format has no state",
            trigger: "select[name='country_id']",
            run: "selectByLabel Germany",
        },
        {
            content: "The state is shown as the country has states",
            trigger: "select[name='state_id']:has(option:contains(Berlin))",
        },
        {
            content: "The fields follow Germany's format, not the previous one",
            trigger: "#div_city + #div_country",
        },
        {
            content: "Select a country whose core format uses state_code",
            trigger: "select[name='country_id']",
            run: "selectByLabel United States",
        },
        {
            content: "The state is shown",
            trigger: "select[name='state_id']:has(option:contains(Alabama))",
        },
        {
            content: "Select a country whose online format omits its required state",
            trigger: "select[name='country_id']",
            run: "selectByLabel Canada",
        },
        {
            content: "The required state is still shown",
            trigger: "select[name='state_id']:has(option:contains(Ontario))",
        },
    ],
});
