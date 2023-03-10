odoo.define("website_sale_product_brand_filter.website", function () {
    "use strict";

    $(document).on("click", ".website_sale_filter_brand_tag_show_more", function (e) {
        e.preventDefault();

        // Hide 'Show more'
        $(this).addClass("d-none");

        // Remove scroll from brands list
        $(".website_sale_filter_brand_tags").removeClass("scroll");

        // Show 'Show less'
        $(".website_sale_filter_brand_tag_show_less").removeClass("d-none");
    });

    $(document).on("click", ".website_sale_filter_brand_tag_show_less", function (e) {
        e.preventDefault();

        // Hide 'Show less'
        $(this).addClass("d-none");

        // Add scroll to brands list
        $(".website_sale_filter_brand_tags").addClass("scroll");

        // Show 'Show more'
        $(".website_sale_filter_brand_tag_show_more").removeClass("d-none");
    });
});
