/* Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CheckoutCountryVatDropdown = publicWidget.Widget.extend({
    selector:
        ".o_wsale_address_fill:has(.js_country_dropdown, select[name=country_id])",
    events: {
        "change select[name=country_id]": "_onChangeAddressCountry",
    },
    start: function () {
        const result = this._super(...arguments);
        this.$address_country = this.$("select[name=country_id]");
        this.$vat_no_country_field = this.$("#no_country_field");
        return result;
    },

    /**
     * Change VAT flag when address country changes
     * @private
     */
    _onChangeAddressCountry: function () {
        if (!this.$address_country || !this.$vat_no_country_field) return;
        if (this.$address_country.val() && !this.$vat_no_country_field.val()) {
            this._getCountryOption(
                this.$address_country.find("option:selected").attr("code")
            ).click();
        }
    },

    /**
     * Get a country element inside the vat dropdown
     *
     * @private
     * @param {String} country_code
     * @returns {jQueryElement}
     */
    _getCountryOption: function (country_code) {
        return this.$(`.js_select_country_code[data-country_code='${country_code}']`);
    },
});
