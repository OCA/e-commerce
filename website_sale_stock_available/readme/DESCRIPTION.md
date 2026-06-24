This module extends the functionality of the *Product Availability*
module (technical name: `website_sale_stock`) so that for the eCommerce
the *Available* quantity of a product is taken into account instead of
the *free* quantity.

Note that in the past the eCommerce availability was based in
*Forecasted quantity*. This isn't true anymore from version 15.0.

If a product is configured to *prevent sales if not enough stock* (see
configuration section) and its page is accessed in the Website Shop, the
availability messages will be based on the *Available* quantity instead
of *Free* quantity. And also, the eCommerce won't allow you to buy more
products than *Available* quantity (not *Free* quantity isn't taken into
account).

## Relation to Odoo 19.0 core

Core 19.0 `website_sale_stock` uses `free_qty` (on-hand minus
reservations) for eCommerce availability. This module swaps in
`immediately_usable_qty` (Available To Promise — includes incoming
moves), which matters for businesses with ongoing inbound supply where
incoming stock should be sellable before it arrives.
