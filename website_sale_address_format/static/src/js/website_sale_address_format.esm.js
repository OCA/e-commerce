/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSale.prototype._changeCountry = function () {
    if (!$("#country_id").val()) {
        return;
    }
    return this.rpc("/shop/country_infos/" + $("#country_id").val(), {
        mode: $("#country_id").attr("mode"),
    }).then(function (data) {
        // placeholder phone_code
        $("input[name='phone']").attr(
            "placeholder",
            data.phone_code !== 0 ? "+" + data.phone_code : ""
        );

        // populate states and display
        var selectStates = $("select[name='state_id']");
        // dont reload state at first loading (done in qweb)
        if (
            selectStates.data("init") === 0 ||
            selectStates.find("option").length === 1
        ) {
            if (data.states.length || data.state_required) {
                selectStates.html("");
                data.states.forEach((x) => {
                    var opt = $("<option>")
                        .text(x[1])
                        .attr("value", x[0])
                        .attr("data-code", x[2]);
                    selectStates.append(opt);
                });
                selectStates.parent("div").show();
            } else {
                selectStates.val("").parent("div").hide();
            }
            selectStates.data("init", 0);
        } else {
            selectStates.data("init", 0);
        }

        // manage fields order / visibility
        if (data.fields) {
            // [CUSTOM][DEL] Following 5 lines
            // if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
            //     $(".div_zip").before($(".div_city"));
            // } else {
            //     $(".div_zip").after($(".div_city"));
            // }
            // [CUSTOM][ADD] Following 5 lines: sort fields according to
            // online_address_format of the country
            var previous_field = $(".div_street");
            data.fields.forEach((field) => {
                previous_field.after($(".div_" + field.split("_")[0]));
                previous_field = $(".div_" + field.split("_")[0]);
            });
            // [CUSTOM][DEL] Following line
            // var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
            // [CUSTOM][ADD] Following line: add street2 and state_code
            var all_fields = [
                "street",
                "street2",
                "zip",
                "city",
                "country_name",
                "state_code",
            ];
            all_fields.forEach((field) => {
                $(".checkout_autoformat .div_" + field.split("_")[0]).toggle(
                    $.inArray(field, data.fields) >= 0
                );
            });
        }

        if ($("label[for='zip']").length) {
            $("label[for='zip']").toggleClass("label-optional", !data.zip_required);
            $("label[for='zip']")
                .get(0)
                .toggleAttribute("required", !!data.zip_required);
        }
        if ($("label[for='zip']").length) {
            $("label[for='state_id']").toggleClass(
                "label-optional",
                !data.state_required
            );
            $("label[for='state_id']")
                .get(0)
                .toggleAttribute("required", !!data.state_required);
        }
    });
};
