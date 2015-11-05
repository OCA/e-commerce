.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Legal terms per product
=======================

This module was written to extend the functionality of e-commerce to support
setting specific legal terms per product and allow you to inform your online
buyers that they are subjected to those when buying that product.

Usage
=====

To create new legal terms, you need to:

* Go to *Sales > Configuration > Product Categories & Attributes > Legal terms
  for products*.
* Create those you need there.
* The contents will be raw rendered to the user, concatenated per product.
* You can choose which products are affected by that legal terms from there.

To assign legal terms to a product, you need to:

* Go to *Sales > Products*.
* Edit or create one.
* Go to *Sales > Sale condition*.
* Use the list *Legal terms* to set the legal terms that affect this product.

To read the legal terms as a buyer, you need to:

* Log out.
* Go to *Shop*.
* Choose a product affected by any legal term.
* You will see a small notice below *Add to Cart*, with a link to the legal
  terms that affect the product.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
e-commerce/issues/new?body=module:%20
{module_name}%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Rafael Blasco <rafaelbn@antiun.com>
* Jairo Llopis <yajo.sk8@gmail.com>

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
