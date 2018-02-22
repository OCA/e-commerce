.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==========================================
Products Custom Information In Online Shop
==========================================

This module extends the functionality of your online shop to support displaying
a "technical datasheet" that outputs the product's custom information, and
allowing the visitor to apply filters on products based on such information.

Installation
============

To install this module, you need to:

#. Install its dependencies, from OCA/server-tools and OCA/product-attributes.

Configuration
=============

There are 2 new places where the custom info filters will appear when you
browse your online shop:

#. *Quick filters*, in the left column.
#. *Advanced filters*, in a modal shown when user clicks that button after the
   search box.

To decide where to put each property:

#. Go to *Custom Info > Advanced > Properties*.
#. Edit or create a property.
#. Select the placement in *Product public filter*. Leave empty to hide this
   property in filters.

In your `online shop </shop>`_ you have now these new templates available under
the *Customize* menu, enabled by default:

- *Custom Info Advanced Filters*, to display the *Advanced filters* button next
  to the search box.
- *Custom Info Quick Filters*, to display the *Quick filters* in the left
  column.

Now, if you enter into any product's page, you will see another template
enabled by default:

- *Display Custom Information*, to show a *Technical datasheet* tab with your
  product's custom information on it, grouped and sorted.

Usage
=====

To see the product custom info in the shop, you need to:

#. Edit a product's custom information (follow instructions in module
   **product_custom_info**).
#. Publish it.
#. See it in the online shop.
#. Click on the new *Technical datasheet* tab.

To apply custom information filters in your shop, you need to:

#. Follow configuration instructions and set some properties to be displayed in
   *quick* and *advanced* sections.
#. Visit your `shop </shop>`_.
#. There you can use the *quick filters* at the left.
   #. If the filter is a checkbox, and you click it, the page is automatically
      updated.
   #. If the filter is any other kind of input, you have to hit *Enter* after
      setting the value to update the page.
   #. *Quick filters* are not available in small viewports.
#. There is also a button to show the *advanced filters* modal, next to the
   search box.
   #. You have to click on *Apply filters* after you change something.
#. Fill some filters and wait until a filtered list of products reloads.

.. warning::
    **Missing some filters?**

    Remember that you will only be able to filter through properties that are
    available among the current list of products.

    So, if you have properties "A" and "B", and the user enters a category, or
    a search query, or any kind of filter that reduces the selection of
    products until no products are left that have the "B" property, then the
    "B" filter will disappear. This is by design, since the user does not need
    to filter in or out by a criteria that will not alter the result.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/9.0

Known issues / Roadmap
======================

* A good improvement would be to display different *quick* filters based on
  current chosen category.

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

.. image:: https://www.tecnativa.com/logo.png
   :alt: Tecnativa
   :target: https://www.tecnativa.com

This module is maintained by Tecnativa.

Tecnativa is an IT consulting company specialized in Odoo and provides Odoo
development, installation, maintenance and hosting services.

To contribute to this module, please visit https://github.com/Tecnativa or
contact us at info@tecnativa.com.
