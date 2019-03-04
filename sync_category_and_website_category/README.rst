.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===================================================
Syncronize internal Categories and website category
===================================================


One way syncronization of internal categories with website categories, all
management is done via internal categories, website categories will be
automatically updated.


Works in conjuction and depends on product_category_attribute_set
and website_sale_product_filter and it syncs also the attributes of private and
public categories.
The module syncs also the category attributes and the associated products so
that public category now is rendered functionally useless, the
website_sale_product_filter module , that works on public categories will seamlessly
work the same.
The one-way sync from private to public category is achieved by hiding all
managment of public (website ) category.
Supports Multi-category provided by product_multi_category for internal_categories, 
while public_categories are natively many2many.


Usage
=====


Known Issues / Roadmap
======================


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
Giovanni Francesco Capalbo <giovanni@therp.nl>

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


