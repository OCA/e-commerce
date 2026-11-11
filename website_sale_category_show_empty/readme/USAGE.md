1.  Go to *Website \> eCommerce \> Products \> eCommerce Categories*.
2.  Open a category and tick *Show When Empty*.

The category page is now reachable for visitors even with no published
product, and renders as an empty category.

Note that the flag governs access to the page only. Shop sidebars and
mega menus filter on `has_published_products` directly rather than
through the record rule, so a flagged empty category is reachable by its
URL but is still left out of those navigation blocks.
