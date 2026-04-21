## Website Sale - Picking Policy

This module extends Odoo eCommerce checkout to let customers choose how
deliverable products are shipped from their cart.

At checkout, a **Shipping Policy** section is added with the available
`picking_policy` options from the sale order (for example, consolidated
delivery in one shipment).

When the customer changes the policy:

- The cart `picking_policy` is updated immediately through a JSON route.
- The estimated delivery date shown in checkout is refreshed when
  relevant.

The policy selector is only displayed when the cart contains deliverable
products.
