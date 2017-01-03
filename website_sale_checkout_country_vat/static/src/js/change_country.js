/* © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

(function ($) {
    "use strict";
    $('.oe_website_sale').each(function () {
        var $this = $(this),
            $country_selector = $this.find("select[name=country_id]"),
            $no_country_field = $this.find("#no_country_field");

        // Change VAT flag when address country changes
        $country_selector.on("change", function (event) {
            if ($country_selector.val() && !$no_country_field.val()) {
                $this.find(".js_select_country_code[data-country_id="
                           + $country_selector.val() + "]")
                     .click();
            }
        });
    });
    $('form[action="/shop/confirm_order"]').on('submit', function(){
        if(!this.no_country_field.value){
            this.vat.value = "";
        }
    });
})(jQuery);
