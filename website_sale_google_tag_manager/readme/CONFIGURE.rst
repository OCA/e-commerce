To configure this module, you need to:

#. Go to **Website > Configuration > Settings**
#. Search 'Google Tag Manager' option.
#. Fill in your 'Google Tag Manager Key' (e.g. 'GTM-ABCDEF').
#. Set 'Enhanced Conversions' on.

With it you can configure your GTM conversion scripts for ``/shop/confirmation``
with the following xpath options:

- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='customer_email']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='customer_name']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='shipping_street']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='shipping_city']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='shipping_zip']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='shipping_region']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='shipping_country']``

Only if you have ``partner_firstname`` installed, you can also use:

- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='customer_firstname']``
- ``//div[@id="gtm_enhanced_conversion_data"]/span[@name='customer_lastname']``

Otherwise you should figure out how to split ``customer_name`` in you js tag scripts.
