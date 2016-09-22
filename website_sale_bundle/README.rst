.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=======================
Product Bundles in Shop
=======================

This module extends the functionality of your online shop to support selling
product bundles.

Configuration
=============

In the product form, you have 2 new optional templates:

.. figure:: website_sale_bundle/static/description/optional_templates.png
  :alt: Included optional templates

- *Bundled Products*, to show products inside a bundle.
- *Display Bundles Including This Product*, to show in which bundles you can
  buy this product.

In the cart view, you have also:

- *Itemize Bundles In Cart*.

Usage
=====

To use this module, you need to:

#. Create a product bundle, as stated in ``product_bundle`` addon.
#. Publish it.
#. See it in the website. It has a new list of bundled products. If any of them
   is published too, it becomes clickable.
#. If you see any bundled product's page, there you can find the bundles that
   include it.

.. figure:: website_sale_bundle/static/description/website_bundle.png
  :alt: Website view of a bundled product that is a bundle

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/9.0

Known issues / Roadmap
======================

* Support product variants when upstream addon does.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jairo Llopis <jairo.llopis@tecnativa.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
