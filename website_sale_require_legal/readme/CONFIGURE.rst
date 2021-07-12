To configure this module, you need to:

#. Install it.

#. Set up `your legal pages </legal>`__.

#. Go to your e-commerce and make a sample checkout.

#. Visit `/shop/address </shop/address>`__ and enable *Customize > Require
   Legal Terms Acceptance*.

   .. figure:: ../static/description/address-enable.png

   This will require acceptance before recording a new address, and log visitor's
   acceptance.

#. Visit `/shop/payment </shop/payment>`__ and enable *Customize > Accept Terms
   & Conditions* (upstream Odoo feature).

   .. figure:: ../static/description/payment-enable.png

   This will require acceptance before paying the sale order, and log visitor's
   acceptance.
