/* Copyright 2025 Tecnativa - Pilar Vargas
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */
import {
    clickOnSave,
    clickOnSnippet,
    insertSnippet,
    registerWebsitePreviewTour,
} from "@website/js/tours/tour_utils";

registerWebsitePreviewTour(
    "product_category",
    {
        url: "/",
        edition: true,
    },
    () => [
        ...insertSnippet({id: "s_product_category", name: "Product Category"}),
        ...clickOnSnippet({id: "s_product_category", name: "Product Category"}),
        ...clickOnSave(),
    ]
);
