Go to Contacts > Configuration > Localization > Countries, and open the country for
which the address field sequence should be adjusted in the eCommerce address page.

Update 'Layout in eCommerce Address Forms' field with something like the below (an
example for Japan):

.. code-block::

  %(country_name)s
  %(zip)s
  %(state_code)s
  %(city)s
  %(street)s
  %(street2)s
