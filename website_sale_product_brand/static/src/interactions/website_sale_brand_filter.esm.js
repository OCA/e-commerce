import {WebsiteSale} from "@website_sale/interactions/website_sale";
import {patch} from "@web/core/utils/patch";
import {rpc} from "@web/core/network/rpc";

patch(WebsiteSale.prototype, {
    start() {
        super.start(...arguments);
        this.setupBrandFilter();
    },

    setupBrandFilter() {
        this.brandFilterForm = this.el.querySelector("form[data-brand-filter-mode]");
        if (!this.brandFilterForm) {
            return;
        }
        const loadMoreButton = this.brandFilterForm.querySelector(
            ".o_wsale_brand_load_more"
        );
        if (loadMoreButton) {
            this.onBrandLoadMore = this.loadMoreBrands.bind(this);
            loadMoreButton.addEventListener("click", this.onBrandLoadMore);
            this.registerCleanup(() =>
                loadMoreButton.removeEventListener("click", this.onBrandLoadMore)
            );
        }
        this.onBrandLetterShown = this.loadBrandLetter.bind(this);
        for (const letter of this.brandFilterForm.querySelectorAll("[data-letter]")) {
            letter.addEventListener("shown.bs.collapse", this.onBrandLetterShown);
            this.registerCleanup(() =>
                letter.removeEventListener("shown.bs.collapse", this.onBrandLetterShown)
            );
        }
        for (const openedLetter of this.brandFilterForm.querySelectorAll(
            "[data-letter].show"
        )) {
            this.loadBrandLetter({currentTarget: openedLetter});
        }
    },

    getBrandRpcParams(extraParams = {}) {
        const url = new URL(window.location.href);
        return {
            search: this.brandFilterForm.dataset.search || "",
            category_id: this.brandFilterForm.dataset.categoryId || false,
            attribute_values: url.searchParams.getAll("attribute_values"),
            brand_ids: [
                ...url.searchParams.getAll("brand"),
                ...url.searchParams.getAll("brand_ids"),
            ],
            ...extraParams,
        };
    },

    async loadMoreBrands(ev) {
        const button = ev.currentTarget;
        button.disabled = true;
        const result = await this.waitFor(
            rpc(
                "/shop/brand_filter/load_more",
                this.getBrandRpcParams({
                    offset: parseInt(button.dataset.offset || "0", 10),
                    limit: parseInt(this.brandFilterForm.dataset.brandLimit || "5", 10),
                    exclude_brand_ids: (button.dataset.excludeBrandIds || "")
                        .split(",")
                        .filter(Boolean),
                })
            )
        );
        this.brandFilterForm
            .querySelector("[data-brand-filter-items]")
            .insertAdjacentHTML("beforeend", result.html);
        if (result.has_more) {
            button.dataset.offset = result.next_offset;
            button.disabled = false;
        } else {
            button.remove();
        }
    },

    async loadBrandLetter(ev) {
        const panel = ev.currentTarget;
        if (panel.dataset.loaded === "1") {
            return;
        }
        const button = panel.querySelector(".o_wsale_brand_letter_load_more");
        const result = await this.waitFor(
            rpc(
                "/shop/brand_filter/load_letter",
                this.getBrandRpcParams({
                    letter: panel.dataset.letter,
                    offset: 0,
                    limit: parseInt(
                        this.brandFilterForm.dataset.brandLetterLimit || "50",
                        10
                    ),
                })
            )
        );
        panel.querySelector("[data-brand-filter-items]").innerHTML = result.html;
        panel.dataset.loaded = "1";
        if (button && result.has_more) {
            button.dataset.offset = result.next_offset;
            button.classList.remove("d-none");
            const onClick = (clickEv) => this.loadMoreBrandLetter(clickEv, panel);
            button.addEventListener("click", onClick);
            this.registerCleanup(() => button.removeEventListener("click", onClick));
        }
    },

    async loadMoreBrandLetter(ev, panel) {
        const button = ev.currentTarget;
        button.disabled = true;
        const result = await this.waitFor(
            rpc(
                "/shop/brand_filter/load_letter",
                this.getBrandRpcParams({
                    letter: panel.dataset.letter,
                    offset: parseInt(button.dataset.offset || "0", 10),
                    limit: parseInt(
                        this.brandFilterForm.dataset.brandLetterLimit || "50",
                        10
                    ),
                })
            )
        );
        panel
            .querySelector("[data-brand-filter-items]")
            .insertAdjacentHTML("beforeend", result.html);
        if (result.has_more) {
            button.dataset.offset = result.next_offset;
            button.disabled = false;
        } else {
            button.remove();
        }
    },

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
