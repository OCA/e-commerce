About search domains
====================

The semantic of the search domains is the regular Odoo’s syntax.

That is, each criterion is a tuple of 3 parts ``(field, operator, value)``. Criteria are assembled into a list of criterion.
 
Example: to search for partners named ABC, from belgium or germany, whose language is not english:

..  code-block:: python

    [('name', '=', 'ABC'),
     ('language.code', '!=', 'en_US'),
     '|',('country_id.code', '=', 'be'),
     ('country_id.code', '=', 'de')
     ]

This domain is interpreted as:
::

    (name is 'ABC')
    AND (language is NOT english)
    AND (country is Belgium OR Germany)

See the official reference at https://www.odoo.com/documentation/8.0/reference/orm.html

However, in the willingness to simplify the API usage, the Web-Service will also accept a simplified form of the criteria, 
which uses string instead of tuples, so the domain above becomes:
::

    ['name = ABC',
     'language.code != en_US',
     '|', 'country_id.code = be',
         'country_id.code = de'
     ]
