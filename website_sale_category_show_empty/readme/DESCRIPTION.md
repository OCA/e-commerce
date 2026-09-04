Odoo hides eCommerce category pages that hold no published product from
public and portal visitors. The record rule
`website_sale.empty_public_categories_rule` restricts them to categories
where `has_published_products` is true, and because the `/shop/category`
route turns the resulting access error into a 404, visitors get a "page
not found" instead of the category page.

That is the wanted behaviour for a catalogue that mirrors stock, but not
for pages that carry editorial content of their own -- a manufacturer or
brand page, for instance, which a shop may want to keep reachable even
while nothing of that brand is published.

This module adds a *Show When Empty* flag on the category. Flagged
categories stay readable for public and portal visitors whatever their
product count.
