This module introduces a scheduled action record that archives wishlist items associated with
inactive (archived) products.

Background:

The default behavior in vanilla Odoo for archived products is as follows:

* Existing wishlist items for the product remain unaffected (they persist in the wishlist).
* When a customer attempts to add the item to their cart, it vanishes from the wishlist and the cart
  remains unchanged.

This behavior can be confusing and may result in customer dissatisfaction.
