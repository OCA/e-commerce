.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Website Sale - One Step Checkout
================================

Description
===========

This module provides an All-In-One checkout for your Odoo customer.

You can activate / deactivate the one step checkout per website.

.. image:: /website_sale_one_step_checkout/static/description/settings.png
    :width: 100%

The checkout page contains all needed information to finish a sale order.

.. image:: /website_sale_one_step_checkout/static/description/osc.png
    :width: 100%

It also keeps your customer on the checkout page while adding or editing an address.

.. image:: /website_sale_one_step_checkout/static/description/address.png
    :width: 100%

One Step Checkout combines all Odoo checkout steps into one and removes all unnecessary fields and
questions. Never before has check-out been easier and faster!

Improving the checkout process results in more customers completing their sales, and this has an immediate impact on your bottom line.
It is the single most effective technical change you can make to reduce shopping cart abandonment.

Installation
============

To install this module, you need to install following module: website_sale_one_step_checkout

Usage
=====

To use this module, you need to:

#. Go to the online shop in the frontend
#. Buy something


Known issues / Roadmap
======================

* For now, this add-on will add a One Step Checkout to the website_sale add-on.
* Check if the One Step Checkout works with website_event_register_free_with_sale.
* Checkout form should have HTML5 validation, but that should be in core or a
  separate module.
* ToDo Controllers: Overwrite /shop/extra_info
* ToDo Controllers: Take care of errors in `proceed_payment`

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Benjamin Bachmann <benniphx@gmail.com>
* Robert Rübner <rruebner@bloopark.de>
* Andrei Poehlmann <andrei.poehlmann90@gmail.com>

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