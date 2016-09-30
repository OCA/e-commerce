.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

==========================
Website Sale - Price Tiers
==========================

This module looks at the price rules for a product and uses them to calculate 
price tiers (quantity ranges with different unit pricing). It then adds radio 
buttons to product pages in the website shop, which allow users to easily
select the minimum quantity corresponding to each tier.

The module also includes the following configurable features:

* An implicit tier with a minimum quantity of 1 added to all products where the
  tiers would not otherwise be empty. This is off by default and can be enabled
  by going to ``Website Admin > Settings`` and selecting the ``Implicit Price
  Tier`` setting under ``eCommerce``.
* Wording added to the unit price shown on product pages to clarify that it is
  a unit price. This is off by default and can be turned on by going to a
  website product page and selecting ``Website Sale - Quantity Tiers (Price
  Wording)`` in the ``Customize`` menu.
* Tier info for each product's lowest price tier in place of unit prices on
  search/browse pages in the shop. This is on by default and can be turned off
  by going to a website shop search page and deselecting ``Website Sale -
  Quantity Tiers in Search`` in the ``Customize`` menu.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/10.0

Known Issues / Roadmap
======================

* Currently, only price rules set up at the product template level will be 
  used to build tiers
* In some cases, the presence of a product variant price rule may cause a tier
  with an overlapping product template price rule to use the product variant
  pricing. For technical details, please see the Python tests in the module.

Bug Tracker
===========

Bugs are tracked on 
`GitHub Issues <https://github.com/OCA/e-commerce/issues>`_. In case of 
trouble, please check there if your issue has already been reported. If you 
spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: 
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Oleg Bulkin <obulkin@laslabs.com>
* Kelly Lougheed <kelly@smdrugstore.com>

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
