/* License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('website_sale_vat_required.tour', function(require) {

    "use strict";

    require("website_sale.tour");
    var base = require("web_editor.base");
    var tour = require("web_tour.tour");
    var steps = tour.tours.shop_buy_product.steps;

    steps.splice(
        _.findIndex(steps, { 'content': "Confirm checkout"}),
        0,
        {
            content: 'Next',
            trigger: ".btn-primary:contains('Next')",
        },
        {
            content: 'Set VAT',
            trigger: "div.has-error input[name='vat']",
            extra_trigger: "div.has-error input[name='vat']",
            run: function (actions) {
                $('div.has-error input[name="vat"]').val("BE0477472701");
                if ($('#div_phone').hasClass('has-error')){
                    $('#div_phone input').val('11111111');
                }
                var input_accept_legal_terms = $('div.has-error input[name="accepted_legal_terms"]');
                if (!_.isUndefined(input_accept_legal_terms && !input_accept_legal_terms== false)){
                    $('div.has-error input[name="accepted_legal_terms"]').prop( "checked", true );
                }
            }
        },
        {
            content: 'Next',
            trigger: ".btn-primary:contains('Next')",
        }
    );
});
