.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

==================================
Website Sale - Alphabetic Category
==================================

This module automatically places each new product in an alphabetic website 
category based on the first character of the product's name. There are two 
catch-all buckets (``#`` for numbers and ``*`` for other non-alphabetic 
characters), and the categories are created on demand, with a shared parent 
category called ``Alphabetical``. 

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/10.0

Known Issues / Roadmap
======================

All unicode characters should be supported, but the module is only intended 
for use with English and may not produce ideal results with other languages 
(e.g. ``É`` will not be grouped with ``E`` or listed between ``E`` and ``F`` 
in the website category menu).

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

* Odoo Community Association: `Icon 
  <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

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
