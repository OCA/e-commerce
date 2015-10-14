Details of get_transfer_status() method
========================================

Goal
----

Return details of outgoing transfers (``stock.picking``).

It always filter only on ``stock.picking`` which are linked to sales orders of the shop (``ecommerce_api_shop.sale_order_ids``).

Additionally, a domain can be provided to narrow the search even more.


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
| method_name | string                 | ``get_transfer_status``                                            |
+-------------+------------------------+--------------------------------------------------------------------+
| shop_ident  | string                 | Shop identifier                                                    |
+-------------+------------------------+--------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.           |
|             |                        |                                                                    |
|             |                        | Example: ``['sale_id = 10']`` or ``[('sale_id', '=', 10)]``        |
+-------------+------------------------+--------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.           |
|             |                        |                                                                    |
|             |                        | Example: ``['id', 'name', 'state', 'carrier_tracking_ref']``       |
|             |                        |                                                                    |
|             |                        | Otherwise, it will return all fields in ``stock.picking`` object   |
+-------------+------------------------+--------------------------------------------------------------------+
| offset      | integer                | Set an offset for reading rows                                     |
+-------------+------------------------+--------------------------------------------------------------------+
| limit       | integer                | Limit number of returned rows                                      |
+-------------+------------------------+--------------------------------------------------------------------+
| order       | string                 | Change ordering of rows (example : ``'create_date asc'``)          |
+-------------+------------------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a list of dictionnary representing ``stock.picking`` objects which correspond to search criterions given in ``domain`` param.

..  code-block:: python

    [
     {'id': 1, 'state': 'done', 'carrier_tracking_ref': 'xyz', 'move_line': [...]},
     {'id': 2, 'state': 'done', 'carrier_tracking_ref': 'abc', 'move_line': [...]},
     ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    transfers = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'get_transfer_status',
        'shop_identifier',
        ['sale_id = 10', 'create_date > 2015-09-24 00:00:00'],
        ['id', 'state', 'carrier_tracking_ref', 'move_line'],
        )
    print transfers
    [{'id': 1, 'state': 'done', 'carrier_tracking_ref': 'xyz', 'move_line': [...]}]


PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    //TODO
    

