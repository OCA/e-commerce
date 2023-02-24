odoo.define("website_sale_filter_product_brand.website", function (require) {
    "use strict";
    var publicWidget = require("web.public.widget");
    publicWidget.registry.WebsiteSaleProductBrandFilter = publicWidget.Widget.extend({
        selector: "#wsale_products_attributes_collapse",
        events: {
            "click .website_sale_filter_brand_tag_show_more": "_onClickShowMore",
            "click .website_sale_filter_brand_tag_show_less": "_onClickShowLess",
        },
        _onClickShowMore: function (event) {
            event.preventDefault();
            this._switchState($(event.currentTarget), false);
            // Show 'Show less'
            this.$(".website_sale_filter_brand_tag_show_less").removeClass("d-none");
        },
        _onClickShowLess: function (event) {
            event.preventDefault();
            this._switchState($(event.currentTarget), true);
            // Show 'Show more'
            this.$(".website_sale_filter_brand_tag_show_more").removeClass("d-none");
        },
        _switchState($element, scroll) {
            $element.addClass("d-none");
            if (scroll) {
                this.$(".website_sale_filter_brand_tags").addClass("scroll");
            } else {
                this.$(".website_sale_filter_brand_tags").removeClass("scroll");
            }
        },
    });
});
