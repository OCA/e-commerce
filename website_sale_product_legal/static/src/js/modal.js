/* © 2015 Antiun Ingeniería, S.L. - Jairo Llopis
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

"use strict";
(function ($) {
    $(".product-legal-terms").click(function(event){
        event.preventDefault();
        dialog = $("<div title='Legal terms'>Loading...</div>")
            .dialog({modal: true});
        $.ajax({
            url: $(event.target).attr("href"),
            success: function(data){
                dialog.html($(data).find("#contents"));
            }
        });
    })
})(jQuery);
