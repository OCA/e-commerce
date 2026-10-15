To use this module, you need to:

1.  Configure *Website Sale Checkout Skip Payment* as documented in that
    module (enable *Checkout Skip Payment* on the website and tick
    *Skip Website Checkout Payment* on the customer).
2.  Optionally adjust the email content in *Settings \> Technical \>
    Email Templates \> Sales: Quotation Sent (Skip Payment)*.
3.  Perform a checkout from the website with that customer.

Expected outcome:

- The order is created in *Sales \> Quotations* in **Quotation** (draft)
  state. No sales order is confirmed and no stock is reserved.
- The customer receives the *Sales: Quotation Sent (Skip Payment)* email.
- The customer's cart is emptied; visiting the shop again starts a new
  cart instead of reopening the just-submitted quotation.
- The quotation is flagged with *Skip-Payment Quotation* so a salesperson
  can identify orders that originated from this flow before confirming
  them manually.
