odoo.define("website_sale_vies_populator", function (require) {
    "use strict";
    const website_sale = require("website_sale.website_sale");

    website_sale.WebsiteSale.include({
        events: _.extend({}, website_sale.WebsiteSale.prototype.events, {
            "change input[name='vat']": "_onChangeVAT",
        }),
        _onChangeVAT: function () {
            const vat = this.$("input[name='vat']").val();
            if (!vat) {
                return;
            }
            this._rpc({
                route: "/website_sale_vies_populator/get_vies_data",
                params: {
                    vat: this.$("input[name='vat']").val(),
                },
            }).then(this.proxy("_handleVIESData"));
        },
        _handleVIESData: function (data) {
            if (!data.vat) {
                return;
            }
            this.$("input[name='company_name']").val(data.name);
            for (const field of ["street", "zip", "city"]) {
                if (!data[field]) {
                    continue;
                }
                this.$(`input[name='${field}']`).val(data[field]);
            }
            this.$(`select[name='country_id'] option[value=${data.country_id}]`).prop(
                "selected",
                true
            );
        },
    });
});
