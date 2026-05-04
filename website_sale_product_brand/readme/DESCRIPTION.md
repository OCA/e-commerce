This module was written to extend the functionality of product filtering
on website. It will allow you to filter product based on its brand.

It also adds brand landing pages under `/shop/brand/<brand-slug>` with
dedicated header and footer content per brand.

The module is multi-website aware: brand landing pages, brand listings,
the website search index, and the sitemap only expose brands that belong
to the current website (or are global). In the backend, the brand form
and list view expose the Website field for users in
`website.group_multi_website` so brands can be assigned to a specific
website.

While shopping online, we have seen various eShops having a feature to
shop by brands which ODOO does not yet provide officially. Website Sale
Product Brand fills the gap at certain extent and by providing basic
search by brands, thus reducing end-user’s efforts in searching the
products he/she wants to purchase.
