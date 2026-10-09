odoo.define("website_account_fiscal_position_partner_type.signup", function (require) {
    "use strict";

    require("auth_signup.signup");

    var publicWidget = require("web.public.widget");

    publicWidget.registry.SignUpForm.include({
        events: _.extend({}, publicWidget.registry.SignUpForm.prototype.events, {
            "change select[name=fiscal_position_type]": "_onChangeFiscalPositionType",
        }),

        _onChangeFiscalPositionType: function (event) {
            if (event.target.value == "b2b") {
                $("#b2c_name_instructions").hide();
                $("#b2b_name_instructions").show();
            } else if (event.target.value == "b2c") {
                $("#b2b_name_instructions").hide();
                $("#b2c_name_instructions").show();
            } else {
                $("#b2b_name_instructions").hide();
                $("#b2c_name_instructions").hide();
            }
        },
    });
});
