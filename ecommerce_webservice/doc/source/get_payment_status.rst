Details of get_payment_status() method
========================================

Goal
----

Return details of invoices (``account.invoice``).

It always filter only on ``account.invoice`` which are linked to sales orders of the shop (``ecommerce_api_shop.sale_order_ids``).

Additionally, a domain can be provided to narrow the search even more. 

:doc:`_about_search_domains`


Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+-------------+------------------------+--------------------------------------------------------------------+
| Argument    | Type                   | Comment                                                            |
+=============+========================+====================================================================+
| dbname      | string                 | name of the database                                               |
+-------------+------------------------+--------------------------------------------------------------------+
| uid         | integer                | Id of the user making the call                                     |
+-------------+------------------------+--------------------------------------------------------------------+
| password    | string                 | password of the user uid                                           |
+-------------+------------------------+--------------------------------------------------------------------+
| model       | string                 | Always ``ecommerce.api.v1``                                        |
+-------------+------------------------+--------------------------------------------------------------------+
| method_name | string                 | ``get_payment_status``                                             |
+-------------+------------------------+--------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.           |
|             |                        |                                                                    |
|             |                        | Example: ``['sale_id = 10']`` or ``[('sale_id', '=', 10)]``        |
+-------------+------------------------+--------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.           |
|             |                        |                                                                    |
|             |                        | Example: ``['id', 'number', 'state']``                             |
|             |                        |                                                                    |
|             |                        | Otherwise, it will return all fields in ``account.invoice`` object |
+-------------+------------------------+--------------------------------------------------------------------+
| offset      | integer                | Set an offset for reading rows                                     |
+-------------+------------------------+--------------------------------------------------------------------+
| limit       | integer                | Limit number of returned rows                                      |
+-------------+------------------------+--------------------------------------------------------------------+
| order       | string                 | Change ordering of rows (example : ``'create_date asc'``)          |
+-------------+------------------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a list of dictionnary representing ``account.invoice`` objects which correspond to search criterions given in ``domain`` param.

..  code-block:: python

    [
     {'id': 31, 'state': 'paid', 'sale_order_id': 10},
     {'id': 12, 'state': 'open', 'sale_order_id': 10},
     ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    payment_status = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'get_payment_status',
        ['sale_id = 10', 'create_date > 2015-09-24 00:00:00'],
        ['id', 'state'],
        )
    print payment_status
    [{'id': 31, 'state': 'paid', 'sale_order_id': 10}]



PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    //TODO
    

