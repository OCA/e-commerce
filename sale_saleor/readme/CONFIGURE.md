Initial Configuration
---------------------

Configure the Saleor account
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open the menu that manages ``saleor.account`` records.
2. Create a new record with at least:

   * **Name**: a descriptive name (for example, ``Saleor Production``).
   * **Saleor Base URL**: the base URL of the Saleor API.
   * **Email / Password**: credentials of a Saleor staff user to obtain JWT
     tokens (or an app token if supported by your setup).
   * **Odoo Base URL**: the public URL of the Odoo instance.

3. Enable the **Active** flag on the account that should be used in
   production. Only one Saleor account can be active at a time.

Once saved, the module will compute webhook target URLs (customer, order,
draft order, payment) from the Odoo base URL. You should configure
corresponding webhooks in Saleor using these URLs and the shared secret.

Configure Saleor channels
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open the ``saleor.channel`` menu.
2. Create a channel and configure:

   * **Name** and **Slug** to match the channel in Saleor.
   * **Status** set to *Active* when the channel is ready to sync.
   * **Currency** and **Default Country** to match Saleor settings.
   * **Shipping Zones** using corresponding Saleor shipping zones.
   * **Warehouses / Locations** that are marked as Saleor warehouses and have a
     remote Saleor warehouse ID.

3. Save the channel. When a channel is created in *Active* status or key
   fields are changed, the connector will automatically synchronize it to
   Saleor.

.. warning::

   Once a channel has been synchronized to Saleor, its currency cannot be
   changed unless explicitly bypassed via technical context.

Configure promotions (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* For loyalty programs and promotions based on ``loyalty.program``:

  * Create programs with ``program_type = 'saleor'``.
  * Configure the discount type (catalogue/order), description, date range,
    rules and channels.
  * Use the *Saleor Promotion Sync* action to push programs to Saleor
    promotions. Batch synchronization is supported.

Configure vouchers (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* For vouchers based on ``saleor.voucher``:

  * Define the voucher type and value, limits, minimum requirements, countries
    and channel listings.
  * Add one or more voucher codes; the module will automatically activate
    codes and set a start date if missing.
  * Use the *Saleor Sync* action on vouchers to push them to Saleor.
