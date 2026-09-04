// Copyright 2020 Tecnativa - Alexandre Díaz

import {Plugin} from "@html_editor/plugin";
import {registry} from "@web/core/registry";

export class ProductCategoryOptionPlugin extends Plugin {
    static id = "websiteSnippetProductCategoryOption";
    resources = {
        clean_for_save_handlers: this.cleanForSave.bind(this),
    };

    cleanForSave({root}) {
        for (const el of root.querySelectorAll(".js_product_category")) {
            el.replaceChildren();
        }
    }
}

registry
    .category("website-plugins")
    .add(ProductCategoryOptionPlugin.id, ProductCategoryOptionPlugin);
