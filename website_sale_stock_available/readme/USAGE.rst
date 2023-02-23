To use this module, you need to:

#. Go to your eCommerce.
#. Select a product that you has been previously configured to *prevent sales
   if not enough stock* for the web product page.
#. Odoo doesn't allow you to add the product to the cart if *Available*
   quantity (not *Free to use* quantity) is equal or less than zero.
   Besides, availability messages will be based on the *Available*
   quantity instead of the *Free to use* quantity.

.. image:: ../static/description/availability_message.png
    :width: 600 px
    :alt: Availability message
