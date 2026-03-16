import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";

patch(WebsiteSale.prototype, {
    onChangeAttribute(ev) {
        const container =
            ev.currentTarget.closest(".o_wsale_products_grid_before_rail") ||
            ev.currentTarget.closest(".oe_website_sale") ||
            document;
        const filters = container.querySelectorAll(
            "form.js_attributes input:checked, form.js_attributes select"
        );
        const attributeValues = new Map();
        const tags = new Set();
        const brands = new Set();
        for (const filter of filters) {
            if (!filter.value) {
                continue;
            }
            if (filter.name === "attribute_value") {
                const [attributeId, attributeValueId] = filter.value.split("-");
                const valueIds = attributeValues.get(attributeId) ?? new Set();
                valueIds.add(attributeValueId);
                attributeValues.set(attributeId, valueIds);
            } else if (filter.name === "tags") {
                tags.add(filter.value);
            } else if (filter.name === "brand") {
                brands.add(filter.value);
            }
        }
        const url = new URL(window.location.href);
        const searchParams = url.searchParams;
        searchParams.delete("attribute_values");
        searchParams.delete("tags");
        searchParams.delete("brand");
        searchParams.delete("brand_ids");
        searchParams.delete("page");

        for (const entry of attributeValues.entries()) {
            searchParams.append(
                "attribute_values",
                `${entry[0]}-${[...entry[1]].join(",")}`
            );
        }
        if (tags.size) {
            searchParams.set("tags", [...tags].join(","));
        }
        for (const brandId of brands) {
            searchParams.append("brand", brandId);
        }

        window.location.assign(`${url.pathname}?${searchParams.toString()}`);
    },
});
