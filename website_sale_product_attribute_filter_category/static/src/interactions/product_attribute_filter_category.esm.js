import {Interaction} from "@web/public/interaction";
import {registry} from "@web/core/registry";

// The $0 copy per category can leave accordions sharing a collapse id.
export class ProductAttributeFilterCategoryIds extends Interaction {
    static selector = ".website_sale_product_attribute_filter_category";

    start() {
        let counter = 0;
        for (const itemEl of this.el.querySelectorAll(".accordion-item")) {
            const collapseEl = itemEl.querySelector(
                ":scope > .collapse, :scope > .accordion-collapse"
            );
            if (!collapseEl || !collapseEl.id) {
                continue;
            }
            const oldId = collapseEl.id;
            const newId = `${oldId}_${counter++}`;
            collapseEl.id = newId;
            for (const triggerEl of itemEl.querySelectorAll(
                `[data-bs-target="#${CSS.escape(oldId)}"]`
            )) {
                triggerEl.setAttribute("data-bs-target", `#${newId}`);
                triggerEl.setAttribute("aria-controls", newId);
            }
        }
    }
}

registry
    .category("public.interactions")
    .add(
        "website_sale_product_attribute_filter_category.product_attribute_filter_category_ids",
        ProductAttributeFilterCategoryIds
    );
registry
    .category("public.interactions.edit")
    .add(
        "website_sale_product_attribute_filter_category.product_attribute_filter_category_ids",
        {Interaction: ProductAttributeFilterCategoryIds}
    );
