To use this module, you must first create at least one affiliate (found in Sales/Affiliate Program).

Once an affiliate has been created, append one of the following to a compatible shop or product url (see below) to track the affiliate's conversions:

* ?aff_ref=\ *affiliate_id*
* ?aff_ref=\ *affiliate_id*\&aff_key=\ *custom_key*

The "affiliate_id" is the ID displayed on the affiliate's record, e.g. "1".

The "custom_key" (optional) is a url-friendly string of your choice used to track a specific campaign, e.g. "anniversary_sale". Associated affiliate requests will be named after this key, if provided.

**Example:** /shop?aff_ref=1&aff_key=anniversary_sale

Compatible URLs
---------------

* /shop
* /shop/category/{category}
* /shop/category/{category}/page/{page}
* /shop/page/{page}
* /shop/product/{product}
