On the eCommerce product page, the "Specifications" table added by
`website_sale_comparison` lists every attribute of the product,
including non-variant-defining ("informative") attributes whose values
can be restricted to specific variant combinations via the attribute
value's "Exclude for" configuration.

Without this module, that table always lists every configured value of
such an attribute, and never updates when the customer changes the
selected variant. This module makes it show only the value(s) actually
compatible with the combination currently selected on the page, and
refreshes that table when the customer changes variant.
