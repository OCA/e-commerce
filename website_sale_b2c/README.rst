.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===================
e-Commerce B2C mode
===================

This module extends the functionality of ``website_sale`` to support B2C
pricing (show prices with taxes included).

Configuration
=============

To configure this module, you need to:

#. Go to *Sales > Configuration > Settings > Quotations & Sales > Sale Price*.
#. Enable *Show line subtotals with taxes included (B2C)*.
#. *Apply*.

Usage
=====

To use this module, you need to:

#. Follow steps in the *Configuration* section above.
#. Edit any product.
#. Go to *Accounting* tab.
#. Set some *Customer Taxes* to it.
#. Publish the product in the website.
#. You will notice the price that appears in the website is computed with
   taxes included.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/9.0

Known issues / Roadmap
======================

* This module is a backport of an Odoo 10.0 feature, so **it will not be
  migrated above that version**.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/e-commerce/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jairo Llopis <jairo.llopis@tecnativa.com>
* David Vidal <david.vidal@tecnativa.com>

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
