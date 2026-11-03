This module extends the functionality of website sale module to keep the
attribute filters in sync with the values the visitor already chose.

Odoo already hides the attribute values that no displayed product uses, but it
computes that list ignoring the chosen values. So, after filtering by a value,
the panel still offers values that belong to products that are no longer
listed. This module narrows those down as well, and hides an attribute whose
values are all gone.
