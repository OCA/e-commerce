.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

========================
Recently Viewed Products
========================

Let the users keep track of the products they saw on the ecommerce.
Uses the session id as a key to store the product history, so it works
for both authenticated and anonymous users

Usage
=====

Open some products pages on the e-commerce, then hover or click on
'Recent Products' in the top menu. You should see a page or a popover (click
vs hover) with your last viewed products.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/50

Known Issues / Roadmap
======================

* 'Add to cart' button near viewed products not already in the cart
* Translations
* Tests
* Configurable options like number of shown results
* Counter near the 'My Products' link, like the cart counter
* Save product views for user if logged in so that they remain saved
  cross-session.
* Backend view of the records and analytics (probably better to split this
  in another module)

Credits
=======

Contributors
------------

* Leonardo Donelli <donelli@webmonks.it>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
