This module keeps attributes that never generate a variant (attributes with
their *Variant Creation* setting on *Never*, e.g. purely informational specs)
out of the website product page's variant selector, and out of the
combination-exclusion rules used to gray out incompatible options.

Without this module, an informational attribute's value can still exclude a
real, variant-defining value through a configured *Exclude for* rule, even
though the informational attribute itself is never shown to the shopper as a
selectable option — resulting in a visible option being grayed out because of
an attribute the shopper cannot see, with a tooltip naming it.

For the same reason, informational values never make a product unsellable:
when their exclusion rules leave no complete combination (e.g. an
informational attribute whose only value is excluded for some variants), the
product page still offers the variants allowed by the variant-defining
attributes, instead of "This product has no valid combination". The same
fallback applies to the first combination of the product wherever it is
used, e.g. the shop grid or the backend product configurator.
