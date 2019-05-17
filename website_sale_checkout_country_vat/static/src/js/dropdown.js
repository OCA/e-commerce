/* Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("website_sale_checkout_country_vat.dropdown", function (require) {
    "use strict";
    var animation = require('website.content.snippets.animation');

    var CheckoutCountryVatDropdown = animation.Class.extend({
        selector: ".oe_website_sale:has(.js_country_dropdown, " +
                  "select[name=country_id])",
        start: function (editable_mode) {
            var result = this._super(editable_mode);
            this.$address_country = this.$("select[name=country_id]");
            this.$vat_no_country_field = this.$("#no_country_field");
            this.$address_country.change(
                $.proxy(this.change_address_country, this)
            );
            return result;
        },

        // Change VAT flag when address country changes
        change_address_country: function () {
            if (
                this.$address_country.val() &&
                !this.$vat_no_country_field.val()
            ) {
                this.get_vat_country_selector(this.$address_country.val())
                    .click();
            }
        },

        // Get a country element inside the vat dropdown
        get_vat_country_selector: function (country_code) {
            return this.$(
                ".js_select_country_code[data-country_id='" +
                country_code + "']"
            );
        },
    });

    animation.registry.website_sale_checkout_country_vat =
        CheckoutCountryVatDropdown;
});
