.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Website Sale Product Brand
==========================

Description
===========

This module was written to extend the functionality of product filtering on website.
It will allow you to filter product based on its brand.

While shopping online, we have seen various eShops having a feature to shop by brands
which ODOO does not yet provide officially.Website Sale Product Brand fills the gap at certain
extent and by providing basic search by brands, thus reducing end-user’s efforts in 
searching the products he/she wants to purchase.

Installation
============

To install this module, you need to install following module:
->https://github.com/OCA/product-attribute/tree/9.0/product_brand

Usage
=====
Shop by brand feature is available on various famous e-commerce websites like amazon, flipkart and many.
Shop by brand feature enables you to display product relevant to that particular brand.

To use this module, you need to:

Once you install this module, user will be able to create a new brand and define the brand to a product.

- To create product brand
    go to:
        sales>products>product brands

User can assign a nice logo with brand description.

- After configuring the brand, user can assign a particular brand to a particular products.

Based on this configuration, you will see the menuitem shop by brand under shop menu.
It will show all the brands and once you select that brand it will show product's which
is related to this brand.

The blog here explains the HOWTO :
    http://www.serpentcs.com/serpentcs-odoo-ecommerce-shop-brands-contribution
The Youtube Video is here :
    https://www.youtube.com/watch?feature=player_embedded&v=LkV5umivylw

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/50

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
e-commerce/issues/new?body=module:%20
website_sale_product_brand%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Jay Vora <jay.vora@serpentcs.com>
* Meet Dholakia <m.dholakia.serpentcs@gmail.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
