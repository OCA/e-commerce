This module requires no configuration: it applies automatically to every
product attribute whose *Variant Creation* is set to *Never*.

1.  On a product, add an attribute with *Variant Creation* set to *Never*
    (e.g. an informational spec such as a material or a care instruction),
    alongside your normal variant-defining attributes.
2.  Optionally, configure an *Exclude for* rule on one of that attribute's
    values, targeting one of the variant-defining values.
3.  Open the product page on the website: the informational attribute no
    longer appears in the variant selector, and the variant-defining value
    targeted by its exclusion rule is no longer grayed out because of it.
4.  Add the product to the cart: the hidden informational attribute never
    blocks *Add to Cart*, even when its excluded or default value would have
    conflicted with the one visibly selected.
