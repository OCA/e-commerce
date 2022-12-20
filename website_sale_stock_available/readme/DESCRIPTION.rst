This module extends the functionality of the *Product Availability* module
(technical name: ``website_sale_stock``) so that for the eCommerce the *Available*
quantity of a product is taken into account instead of the *free* quantity.

Note that in the past the eCommerce availability was based in *Forecasted quantity*. This
isn't true anymore from version 15.0.

If a product is configured to *prevent sales if not enough stock*
(see configuration section) and its page is accessed in the Website Shop,
the availability messages will be based on the *Available* quantity instead of
*Free* quantity. And also, the eCommerce won't allow you to buy more products than
*Available* quantity (not *Free* quantity isn't taken into account).
