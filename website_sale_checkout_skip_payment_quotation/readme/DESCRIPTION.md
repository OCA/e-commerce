This module extends *Website Sale Checkout Skip Payment* so that, when a
logged-in customer with the *Skip Website Checkout Payment* flag completes
the website checkout:

- the order is **not** automatically confirmed and stays in *Quotation*
  (draft) state, waiting for a salesperson to review it;
- a dedicated email template (*Sales: Quotation Sent (Skip Payment)*) is
  sent to the customer to acknowledge the request, instead of the standard
  sale order confirmation email;
- the order is flagged so the website cart resolver will **not** resurrect
  it as the customer's active cart on subsequent visits. The customer
  starts from an empty cart on their next visit.

This is useful for B2B scenarios where every order has to be reviewed by
a salesperson before it is confirmed, while still letting the customer
finalise the checkout flow without going through a payment step.
