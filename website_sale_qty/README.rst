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

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/9.0

Known Issues / Roadmap
======================

* Currently, only price rules set up at the product template level will be 
  used to build tiers
* In some cases, the presence of a product variant price rule with the same 
  minimum quantity as a product template price rule may cause the tier 
  corresponding to that product template price rule to not show up. For 
  technical details, please see the Python tests in the module.

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
