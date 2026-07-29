During the standard checkout, customers walk through the Order, Address and
Extra Info steps before reaching the payment page. Returning customers who
already have a valid address on file rarely need to revisit those intermediate
steps.

This module inserts a secondary "Payment" button next to the main confirmation
button on every non-payment checkout step. Clicking it navigates directly to
`/shop/payment`, skipping the steps in between. The button is rendered only on
the Order, Address and Extra Info pages and never on the payment page itself.
