To configure this module, you need to:

#. Go to *Website > Configuration > Settings*
#. Select the website you want to configure.
#. In the *Product* section there's a *Sort Criteria* option that you
   can set as the default one for the website selected.

To extend the module you can override the method providing sorting options like
this:

  .. code-block:: python

    @api.model
    def _get_product_sort_criterias(self):
      res = super()._get_product_sort_criterias()
      return res.append(("default_code asc", _("Reference - A to Z")))
