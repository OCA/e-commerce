import {ProductRow} from "@website_sale_comparison/js/product_row/product_row";

ProductRow.props = {
    ...ProductRow.props,
    website_hide_price: {type: Boolean, optional: true},
};
