This module keeps attributes that never generate a variant (attributes with
their *Variant Creation* setting on *Never*, e.g. purely informational specs)
out of the website product page's variant selector, and out of the
combination-exclusion rules used to gray out incompatible options.

Without this module, an informational attribute's value can still exclude a
real, variant-defining value through a configured *Exclude for* rule, even
though the informational attribute itself is never shown to the shopper as a
selectable option — resulting in a visible option being grayed out because of
an attribute the shopper cannot see, with a tooltip naming it.
