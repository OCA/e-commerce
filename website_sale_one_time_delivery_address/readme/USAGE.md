To use this module, you need to:

1.  Add products to the cart and go to the checkout.
2.  In the delivery section, enable *One-Time Delivery Address*.
3.  Enter the final recipient address.
4.  Submit the delivery address form.

Result:

- a child contact is created on the reseller with type
  `one_time_delivery`
- the sale order shipping partner points to that new contact
- the sale order invoice partner remains the reseller, even if the
  browser submits a delivery-as-billing value
- the *Same as delivery address* toggle is hidden while the option is
  enabled, so the temporary delivery address can never be reused as the
  billing address

If the shopper disables the option, the standard website sale delivery
address behavior is kept and a regular `delivery` address is created
instead.

## Automatic archiving

One-time delivery contacts are temporary by nature. As soon as the sale
order is confirmed, its `one_time_delivery` shipping contact is
automatically archived so it stops cluttering the address book. Archiving
is reversible and the contact remains readable on the related stock
pickings and order history.
