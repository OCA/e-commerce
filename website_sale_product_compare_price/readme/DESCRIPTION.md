This module shows, on the product page of the e-commerce, how much the
shopper saves when the effective price of a product is lower than its
reference price:

- a crossed-out reference price,
- a discount badge with the percentage, and
- the amount saved.

Two references are supported, following the native `website_sale` behaviour:

- the sales price of the variant (list price + price extra), when a pricelist
  rule that is not shown natively (e.g. a fixed price per product or variant)
  lowers the effective price;
- the manual *Compare to Price* field of the product template.

The block is only rendered when the *Comparison Price* feature of the
e-commerce is enabled and it stays in sync when the shopper selects another
variant. The reference price is loaded with the same taxes as the sale price,
so the comparison is coherent in both tax-excluded and tax-included shops.
