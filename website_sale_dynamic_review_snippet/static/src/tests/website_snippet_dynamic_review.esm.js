import {
    clickOnSave,
    insertSnippet,
    registerWebsitePreviewTour,
} from "@website/js/tours/tour_utils";

registerWebsitePreviewTour(
    "dynamic_review",
    {
        url: "/",
        edition: true,
    },
    () => [
        ...insertSnippet({id: "s_dynamic_review_snippet", groupName: "Products"}),
        ...clickOnSave(),
    ]
);
