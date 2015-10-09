Details of get_inventory() method
=================================

Goal
----

Retrieve available and virtual quantities for a list of product ids.

Returns the current quantity in stock for all products or for a list of products. The quantity fields returned are: ``quantity_available``, ``virtual_available``.



Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+-------------+-----------------+--------------------------------------------------------------------+
| Argument    | Type            | Comment                                                            |
+=============+=================+====================================================================+
| dbname      | string          | name of the database                                               |
+-------------+-----------------+--------------------------------------------------------------------+
| uid         | integer         | Id of the user making the call                                     |
+-------------+-----------------+--------------------------------------------------------------------+
| password    | string          | password of the user uid                                           |
+-------------+-----------------+--------------------------------------------------------------------+
| model       | string          | Always ``ecommerce.api.v1``                                        |
+-------------+-----------------+--------------------------------------------------------------------+
| method_name | string          | ``get_inventory``                                                  |
+-------------+-----------------+--------------------------------------------------------------------+
| product_ids | list of integer | Filter on a selection of products. If empty, returns all products. |
+-------------+-----------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a dictionnary indexed by product_ids given in parameters.

..  code-block:: python

    {'product_id1': {'quantity_available': qty_available,
                     'virtual_available': virtual_available
                     },
     ...
     }

Python call example
-------------------
..  code-block:: python
   :linenos:

    quantities = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'get_inventory',
        [1, 2]
        )
    print quantities
    {1: {'quantity_available': 10, 'virtual_available': 8},
     2: {'quantity_available': 0, 'virtual_available': 0}
    }

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    //TODO
    

