import {BaseOptionComponent} from "@html_builder/core/utils";
import {Plugin} from "@html_editor/plugin";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";

export class ShopProductReferenceOption extends BaseOptionComponent {
    static template =
        "website_sale_product_reference_displayed.ShopProductReferenceOption";
    static selector = "main:has(#o_wsale_container)";
    static title = _t("Products Page");
    static editableOnly = false;
}

export class ProductPageReferenceOption extends BaseOptionComponent {
    static template =
        "website_sale_product_reference_displayed.ProductPageReferenceOption";
    static selector = "main:has(.o_wsale_product_page)";
    static title = _t("Product Page");
    static editableOnly = false;
}

class ProductReferenceOptionPlugin extends Plugin {
    static id = "productReferenceOptionPlugin";

    resources = {
        builder_options: [ShopProductReferenceOption, ProductPageReferenceOption],
    };
}

registry
    .category("website-plugins")
    .add(ProductReferenceOptionPlugin.id, ProductReferenceOptionPlugin);
