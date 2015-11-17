/* © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */


(function () {
    'use strict';

    var snippet = openerp.website.snippet;

    snippet.animationRegistry.legal_terms_modal = snippet.Animation.extend({
        selector: ".js_legal_terms",
        start: function(editable_mode) {
            this.$target.on("show.bs.modal", this.on_modal_show);
        },
        on_modal_show: function (event) {
            $.ajax({
	            url: $(event.relatedTarget).attr("href"),
	            success: function(data){
	                $(event.currentTarget)
                    .find(".modal-body")
                    .html($(data).find("#contents"));
	            }
	        });
        },
    });
})();
