odoo.define("website_sale_stock_picking_note.payment", function (require) {
    "use strict";

    var ajax = require("web.ajax");

    $(document).ready(function () {
        $("button#o_payment_form_pay").bind("click", function (ev) {
            var picking_note = $("#picking_note").val();
            ajax.jsonRpc("/shop/customer_comment/", "call", {
                picking_note: picking_note,
            });
        });
    });
});
