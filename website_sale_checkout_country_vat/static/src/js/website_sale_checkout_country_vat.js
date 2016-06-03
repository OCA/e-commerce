/* © 2016 Tecnativa, S.L.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
'use strict';
(function ($) {
    var website = openerp.website,
        qweb = openerp.qweb;

    website.snippet.animationRegistry.checkoutVat = website.snippet.animationRegistry.countryDropdown.extend({
        selector: ".js_country_checkout_vat",
        start: function () {
            this._super();
        },
    });
})(jQuery);
