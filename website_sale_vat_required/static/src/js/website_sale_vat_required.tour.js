/* License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
odoo.define('website_sale_vat_required.tour', function(require) {
    "use strict";

    require("website_sale.tour");
    var tour = require("web_tour.tour");
    var steps = tour.tours.shop_buy_product.steps;

    steps.splice(
        _.findIndex(steps, { 'content': "go to checkout"}) + 1,
        0,
        {
            content: 'Next',
            trigger: ".btn-primary :contains('Next')",
        },
        {
            content: 'Set VAT',
            trigger: "div.o_has_error label[for='vat']",
            extra_trigger: "div.o_has_error label[for='vat']",
            run: function (actions) {
                $('div.o_has_error input[name="vat"]').val("US01234567891");
                if ($('#div_phone').hasClass('o_has_error')){
                    $('#div_phone input').val('11111111');
                }
                $('div.o_has_error input[name="accepted_legal_terms"]').prop("checked", true);
            }
        },
        {
            content: 'Next',
            trigger: ".btn-primary :contains('Next')",
        },
        {
            content: 'Confirm',
            trigger: ".btn-primary :contains('Confirm')",
        }
    );
});
