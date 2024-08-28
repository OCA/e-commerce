odoo.define(
    "website_sale_product_attachment.tour",
    ["web_tour.tour"],
    function (require) {
        "use strict";

        var tour = require("web_tour.tour");

        tour.register(
            "website_sale_product_attachment_tour",
            {
                test: true,
                url: "/shop",
                stepDelay: 500,
            },
            [
                {
                    trigger: "a:contains('Customizable Desk')",
                },
                {
                    trigger: "a:contains('Product downloads')",
                },
            ]
        );
        return {};
    }
);
