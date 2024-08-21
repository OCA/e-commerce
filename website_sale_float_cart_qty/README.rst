.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Website Sale Float Cart Quantity
================================

Overview
--------

This module extends the functionality of the `website_sale` module in Odoo by allowing float quantities in the shopping cart instead of integer quantities.

Features
--------

- Enables users to add fractional quantities of products to the shopping cart.
- Overrides the `_changeCartQuantity` function from `website_sale` to handle float quantities.
- Uses `parseFloat` instead of `parseInt` for value conversion on the client-side.

Usage
-----

- Users can add decimal quantities of products to the shopping cart from the online store.

- Quantities are dynamically updated in the user interface after each quantity change.

Development
-----------

The `website_sale_float_cart_qty` module uses JavaScript to extend the functionality of Odoo's `website_sale` module. The `website_sale_float_cart_qty.js` file overrides the `_changeCartQuantity` function to handle float quantities and perform server communication via RPC.

Contributions
-------------

Contributions are welcome! If you want to contribute to the development of this module, feel free to submit a pull request or report issues on the official repository.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/avanzosc/odoo-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Ana Juaristi <anajuaristi@avanzosc.es>
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.
