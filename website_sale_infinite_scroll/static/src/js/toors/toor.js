odoo.define("website_sale_infinite_scroll.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var ajax = require("web.ajax");

    var steps = [
        {
            trigger: "#wrapwrap",
            run: function () {
                const url = "/website_sale_infinite_scroll/page/2";
                ajax.post(url, {async: true}).then(function (table) {
                    console.log(table);
                });
            },
        },
        {
            trigger: "#wrapwrap",
            run: function () {
                window.location.href = "/shop";
                const url = "/website_sale_infinite_scroll/page/1000?ppg=False";
                ajax.post(url, {async: true}).then(function (table) {
                    console.log(table);
                });
            },
        },
    ];
    tour.register(
        "website_sale_infinite_scroll",
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
