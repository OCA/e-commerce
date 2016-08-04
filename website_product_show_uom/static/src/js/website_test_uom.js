(function () {
    'use strict';
    openerp.Tour.register({
        id:   'website_test_uom',
        name: "Test if the UoM appears on every user",
        path: '/shop',
        mode: 'test',
        steps: [
            {
                title:  "search ipod",
                element: 'form:has(input[name="search"]) a.a-submit',
                onload: function() {
                    $('input[name="search"]').val("ipod");
                }
            },
            {
                title:     "select ipod",
                waitFor:    "div.product_price span:contains(Unit(s))",
                waitNot:    "section a:contains(iPad Retina Display)",
                content:    "This step checks that after searching the unit of measure appears on the div that contains the ipod",
                element:   '.oe_product_cart a:contains("iPod")',
            },
            {
                title:     "Finish",
                content:    "This step checks that after clicking on the ipod that the price is displayed correctly and finishes the test",
                waitFor:    "section#product_detail div.product_price span:contains(Unit(s))",
            },
        ]
    });

}());
