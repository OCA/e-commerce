odoo.define("website_sale_filter_product_brand.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    var steps = [
        {
            trigger: "body",
            run: function () {
                const chbox = document.querySelectorAll(
                    "ul li label input[name=brand]"
                );
                if (chbox) {
                    for (const ch of chbox) {
                        ch.click();
                    }
                }

                window.location.href = "/shop";
            },
        },
    ];
    tour.register(
        "website_sale_filter_product_brand",
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
