/* Copyright 2020 Alexandre D. Díaz
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define("website_sale_attribute_filter_category_collapsable.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");
    var base = require("web_editor.base");
    var filterCategorySteps = require("website_sale_attribute_filter_category.tour").steps;

    tour.register("website_sale_attribute_filter_category_collapsable",
        {
            url: "/shop",
            test: true,
            wait_for: base.ready(),
        },
        filterCategorySteps
    );
    return {
        steps: filterCategorySteps,
    };
});
