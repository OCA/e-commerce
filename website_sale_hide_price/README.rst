.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Website Sale Hide Price
=======================

This module allows to have hidden product prices on the website store.

Configuration
=============

#. Go to *Customers* and choose one.
#. Go to *Sales and Purchases* tab.
#. In *Sales* group set *Show prices on website* on or off so this customer can
   see them or not. The default value is `True`, so every partner website user
   can see the prices.
#. If you wanted to have the prices hidden by default when no user is logged
   in you should go to Public User's partner and set *Show prices on website*
   off.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/113/12.0

Known issues / Roadmap
======================

- This feature doesn't support multi website. The default behavior is to hide the prices
  along every website. It could be modified the boolean field on the partner to a many2many
  relation between res_partner and website_website, so that this price-hiding feature might
  be made website-dependant.

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

* David Vidal <david.vidal@tecnativa.com>
* Abraham González <abraham@trey.es>
* Juanjo Algaz  <jalgaz@gmail.com>

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
