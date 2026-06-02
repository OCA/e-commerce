This module makes the website product search render the result title from
`display_name` instead of `name`.

By default the website search (the autocomplete dropdown and the
`/website/search` results page) shows the product template `name`, whereas
the rest of the eCommerce (shop grid, product page) uses `display_name`, which
prepends the internal reference (`default_code`) when the
`display_default_code` context flag is set.

As a result, a product reached through the search bar drops its reference even
though `default_code` and `variants_default_code` are already searchable. This
module makes the search results consistent with the rest of the shop and
exposes the product reference.
