odoo.define("ecommerce_first_last_name.website_state", function (require) {
    "use strict";

    var sAnimations = require("website.content.snippets.animation");

    sAnimations.registry.WebsiteAnimate.include({
        read_events: _.extend(
            {},
            sAnimations.registry.WebsiteAnimate.prototype.read_events,
            {
                "change #company_type_individual": "_onChangeCompanyType",
                "change #company_type_company": "_onChangeCompanyType",
            }
        ),
        _onChangeCompanyType: function (ev) {
            var company = document.getElementById("address_company_name");
            var vat = document.getElementById("address_tin_vat");

            if ($(ev.currentTarget).val() === "company") {
                company.style.display = "block";
                if (vat) {
                    vat.style.display = "block";
                }
            } else {
                company.style.display = "none";
                if (vat) {
                    vat.style.display = "none";
                }
            }
        },
    });
});
