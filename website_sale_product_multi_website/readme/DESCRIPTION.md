This module extends that behavior by allowing products to be linked to
multiple websites through a new `website_ids` field. It also adapts the
website publication and access logic so products are only available on
the selected websites.

This is useful in multi-website environments where the same catalog item
must be shared across some websites, but not all of them.
