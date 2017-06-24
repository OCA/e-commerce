odoo.define("website_sale_recently_viewed_products.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");


    var item = "div[itemtype='http://schema.org/Product']",
        ipod = item + ":contains(iPod)",
        imac = item + ":contains(iMac)";


    tour.register("test_website_sale_recently_viewed_products", {
            name: "Look at some products and check your recently viewed products",
            test: true,
            url: "/shop",
            wait_for: base.ready()
        },
        [
            {
                content: "Let me checkout the iPod, no viewed products so far",
                trigger: ipod,
                run: function(){
                    if ($("[href='/shop/recent']:visible").length){
                        console.log('error')
                    }
                },
            },
            {
                content: "Let me go back to checkout another thing",
                trigger: "a[href='/shop']",
                run: "click",
            },
            {
                content: "Let me checkout the iMac",
                trigger: imac,
                run: "click",
            },
            {
                content: "Let me checkout my recently viewed products",
                trigger: "a[href='/shop']",
                run: "click",
            },
            {
                content: "Should contain iPod and iMac",
                extra_trigger: "a[href='/shop/product/ipod-18']",
                trigger: "a[href='/shop/product/e-com09-imac-15']"
            }

        ])

});
