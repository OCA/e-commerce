/* Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('website_sale_vat_required.tour', function (require) {
    "use strict";

    require("website_sale.tour");
    var buy_tour = require('web.Tour').tours["shop_buy_product"];

    buy_tour.steps.forEach(function (value, index) {
        // Search upstream tour step that would fail with this addon installed
        if (value.title === "test without input error") {
            // Patch step's `onload` method
            var oldonload = value.onload;
            value.onload = function () {
                // Fill VAT field with a good value
                $('.has-error > input[name="vat"]').val("BE0477472701")
                return oldonload.apply(this, arguments);
            };
            return false;
        }
    });
});
