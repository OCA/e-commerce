This module is a backport of the standard implementation Odoo introduces in
version 19.3, see
[odoo/odoo@d2648b1](https://github.com/odoo/odoo/commit/d2648b1d983927b5df7260a16d6d1d33c213ddeb#diff-5a563f36ffd028b0d8510c6d1339b097a5067a2247cc35c0f9bdd1fd0b5a0b0).

This module shows the price of each packaging on the eCommerce product page.

When a product is sold in several packagings, hovering a packaging button
displays the price of that packaging for the quantity currently selected,
so that customers can compare packagings without switching between them.

It is the eCommerce counterpart of `product_pricelist_item_uom`, which
allows a pricelist rule to be restricted to a specific packaging, and is
installed automatically when both that module and `website_sale` are installed.
