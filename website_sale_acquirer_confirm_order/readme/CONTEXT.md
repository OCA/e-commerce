This module adds the option “Confirm Order Automatically” to the website's payment providers.
It is intended only for payment methods that require manual confirmation, such as bank transfer or equivalent custom methods (e.g., money orders or cash on delivery managed outside of Odoo).

When this option is enabled, the sales order is automatically confirmed after checkout is completed, without waiting for payment reconciliation.

It should not be enabled for online payment gateways (Stripe, Redsys, PayPal, etc.), as these automatically confirm the order when the transaction is authorized. Enabling it in these cases could result in duplicate or premature confirmations.
