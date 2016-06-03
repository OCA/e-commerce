/* © 2016 Tecnativa, S.L.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
(function () {
    'use strict';
    var website = openerp.website,
        qweb = openerp.qweb;

    if (!website.snippet) website.snippet = {};
    website.snippet.animationRegistry.vat_code = website.snippet.Animation.extend({
        selector: ".js_vat_dropdown",
        start: function () {
            var self = this;
            this.$target.on('click', '.select_vat_code', function($event) {
                $('#country_vat_code').val($event.currentTarget.id);
                $("#img_code_vat").attr("src", "/website/image/res.country/"+ $event.currentTarget.dataset.country_id +"/image/32x32");
                $('#btn_vat_code').val($event.currentTarget.data('country_id'));
            });
        },
    });
})();
