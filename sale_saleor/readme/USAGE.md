Requirements
------------

* A running Saleor instance reachable from the Odoo server.
* An Odoo URL that Saleor can reach in order to call webhooks.


Main Flows
----------

Pushing orders from Odoo to Saleor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This flow is used when orders are created in Odoo but should also exist in
Saleor:

1. Create a ``sale.order`` in Odoo as usual.
2. Set the **Saleor Channel** field to a synced ``saleor.channel``.
3. Ensure all products that must be sent to Saleor have a
   ``saleor_variant_id``.
4. Use the *Sync to Saleor* action on the order.

The connector will:

* Build the order payload including billing/shipping addresses, order lines
  (variant and quantity) and customer identity (user or email).
* Create or update a draft order in Saleor, apply the shipping method and
  complete the order.
* Store the ``saleor_order_id`` on the Odoo order and post links to the Saleor
  dashboard in the chatter.

You can also use the *Mark paid in Saleor* action to notify Saleor that the
order has been paid in Odoo (for example, offline payments).

Note:
   For customers in certain countries (for example, US/CA), a state/province
   may be required. The connector validates this and raises an error if needed
   information is missing.

Receiving orders and updates from Saleor (webhooks)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When Saleor is the main source of order creation:

1. In Saleor, configure webhooks:

   * **Order created/updated** → ``/saleor/webhook/order_created_updated``.
   * **Order paid / fully paid** → ``/saleor/webhook/order_payment``.

2. Use the same App/account and secret that are stored on the
   ``saleor.account`` in Odoo.

When events occur:

* ``ORDER_CREATED`` / ``ORDER_UPDATED``:

  * Odoo fetches the full order from Saleor.
  * The connector creates or updates a ``sale.order`` in Odoo.
* ``ORDER_PAID`` / ``ORDER_FULLY_PAID``:

  * The connector locates the related ``sale.order`` using
    ``saleor_order_id``.
  * Payment-related fields are updated and a message is posted in the chatter.

Orders explicitly marked as originating from Odoo (metadata ``odoo_origin``)
are ignored by the webhook flow to avoid loops.

Abandoned cart / quotation handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The cron method ``cron_mark_abandoned_saleor_orders`` periodically:

* Finds Saleor-origin quotations (with ``saleor_order_id``) still in
  ``draft``/``sent`` state and not yet marked as abandoned.
* Compares their age with the ``abandoned_cart_delay_hours`` configured on the
  related ``saleor.channel``.
* Marks qualifying quotations as abandoned and posts an explanatory message on
  each order.

Stock Synchronization
---------------------

The connector exposes a job to update Saleor product variant stock quantities
by warehouse (``job_variant_stock_update``) to push stock changes to Saleor.

Best Practices
--------------

* Keep exactly one ``saleor.account`` active to avoid ambiguity when
  processing webhooks.
* Ensure ``odoo_base_url`` points to the external URL that Saleor can reach
  and configure SSL verification appropriately.
* Avoid changing channel currencies after initial synchronization.
* Regularly verify that product variants, warehouses and locations are synced
  and have their corresponding Saleor IDs.
* Monitor logs and queue jobs for synchronization errors and fix data issues
  early.

