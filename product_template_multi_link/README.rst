.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=============================
Product Multi Link (Template)
=============================

This module extends the functionality of sale module to support links between
products templates.

This module adds two types of links :

- **Cross Selling** : suggest your customer to purchase an additional product
- **Up Selling** : suggest your customers to purchase a higher-end product,
  an upgrade, etc.

These types of links are common in e-commerce shops.

It can be used as a base to implement synchronizations with e-commerce.

Important Note
--------------

This module is linking products together (product templates), not product
variants. For that purpose, you can use the module Product Multi Link
(Variants), in the same OCA / e-commerce repository.

Usage
=====

* To mass edit or create links between products templates, Go to
  Sale > Configuration > Products > Product Links

.. figure:: /product_template_multi_link/static/description/product_template_link_tree.png
   :width: 800 px

A kanban view is also available

.. figure:: /product_template_multi_link/static/description/product_template_link_kanban.png
   :width: 800 px


* You can manage links by product, Go to Sales > Sales > Products and select
  a product

.. figure:: /product_template_multi_link/static/description/product_template_form.png
   :width: 800 px

* You can so add new item, line by line, via an editable tree view

.. figure:: /product_template_multi_link/static/description/product_template_link_tree_edit.png
   :width: 800 px


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Known issues / Roadmap
======================

* This module links templates together. 'product_multi_link' links variants
  together. We could, in a next version of Odoo, include variants features
  in that module, and adding a new group in 'Manage Product Variant Links'.

* Develop another module product_template_multi_link_customer, that adds
  a new type of link named 'customer'. Those links could be generated
  automatically by scheduled cron task, analyzing sale.order.line.
  Odoo could create so, the 3 most products sold when a given product is
  sold.

Credits
=======

Images
------

* https://www.iconfinder.com/icons/285808/auto_automobile_car_vehicle_icon
* https://www.iconfinder.com/iconsets/kitchen-appliances-computers-and-electronics

(Free for commercial Use)

Contributors
------------

* Sylvain LE GAL <http://www.twitter.com/legalsylvain>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité <http://www.grap.coop>

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
