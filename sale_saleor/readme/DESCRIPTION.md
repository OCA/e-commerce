Saleor Connector for Odoo
==========================

The ``sale_saleor`` module provides a two-way connector between Odoo and the
Saleor e-commerce platform. It focuses on synchronizing sales channels, orders,
payments, promotions, and vouchers while keeping Odoo as the central business
backend, with explicit flows in both directions:

* From Odoo to Saleor: push sales orders, payment status, product variant
  stock levels by warehouse, loyalty programs and vouchers defined in Odoo.
* From Saleor to Odoo: receive orders, order updates and payment events via
  webhooks and reflect them in ``sale.order`` records in Odoo.

Scope
-----

This module does not replace Odoo's standard sales and inventory flows. Instead,
it extends them so that you can:

* Link a single Saleor account to your Odoo database.
* Synchronize Saleor channels with Odoo currencies, countries, warehouses and
  locations.
* Exchange order and payment information between Saleor and Odoo.
* Push Odoo loyalty programs and vouchers to Saleor promotions and vouchers.
* Mark Saleor-origin quotations as abandoned in Odoo based on per-channel
  delays.

Key Features
------------

* **Saleor account management (``saleor.account``)**

  * Stores the Saleor base URL, credentials and SSL verification settings.
  * Automatically generates webhook target URLs (customer, order, draft order,
    payment) from the configured Odoo base URL.
  * Manages the Saleor App ID, token, webhook IDs and shared secret used for
    HMAC verification.
  * Enforces that only one Saleor account can be active at a time.

* **Saleor channels (``saleor.channel``)**

  * Maps Saleor channels to Odoo currencies, default countries, shipping
    zones, warehouses and locations.
  * Synchronizes channels to Saleor, including linked warehouses/locations that
    are marked as Saleor warehouses.
  * Prevents changing the currency once a channel has been synced to Saleor
    (unless explicitly bypassed from context).
  * Provides a cron job to mark Saleor quotations as abandoned based on a
    channel-specific delay.

* **Sales orders (``sale.order``)**

  * Extends sales orders with fields such as ``saleor_order_id``,
    ``saleor_channel_id`` and detailed Saleor payment state.
  * Provides an action to push orders from Odoo to Saleor by creating and
    completing a draft order with addresses and order lines.
  * Provides an action to mark the related Saleor order as paid from Odoo.
  * Validates required data before syncing (Saleor channel, product variants,
    address requirements for specific countries, etc.).

* **Webhooks from Saleor**

  * ``/saleor/webhook/order_created_updated`` handles ``ORDER_CREATED`` and
    ``ORDER_UPDATED`` events:

    * Fetches full order details from Saleor via API.
    * Skips orders that are explicitly marked as originating from Odoo in
      metadata (to avoid loops).
    * Creates or updates the corresponding ``sale.order`` in Odoo.

  * ``/saleor/webhook/order_payment`` handles ``ORDER_PAID`` and
    ``ORDER_FULLY_PAID`` events:

    * Locates the related ``sale.order`` using ``saleor_order_id``.
    * Updates payment-related fields and posts messages on the order.

* **Promotions and loyalty programs (``loyalty.program``)**

  * Supports programs of type ``saleor``.
  * Builds a minimal promotion payload (type, description, validity dates) to
    reduce compatibility issues across Saleor versions.
  * Synchronizes programs to Saleor promotions and upserts promotion rules.

* **Saleor vouchers (``saleor.voucher``)**

  * Prepares Saleor voucher payloads including discount type/value, date and
    usage limits, countries, channel listings and requirements.
  * Collects and sends voucher codes, and adds additional codes after
    creation/update when needed.
  * Automatically activates voucher codes and ensures a start date is set.

* **Stock and variants**

  * Provides a job to update Saleor variant stock quantities by warehouse.

