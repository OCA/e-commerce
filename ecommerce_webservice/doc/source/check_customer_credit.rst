Details of check_customer_credit() method
=========================================

Goal
----

Return the credit total amount of customers.

Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+--------------+-----------------+--------------------------------------------------------------------+
| Argument     | Type            | Comment                                                            |
+==============+=================+====================================================================+
| dbname       | string          | name of the database                                               |
+--------------+-----------------+--------------------------------------------------------------------+
| uid          | integer         | Id of the user making the call                                     |
+--------------+-----------------+--------------------------------------------------------------------+
| password     | string          | password of the user uid                                           |
+--------------+-----------------+--------------------------------------------------------------------+
| model        | string          | Always ``ecommerce.api.v1``                                        |
+--------------+-----------------+--------------------------------------------------------------------+
| method_name  | string          | ``check_customer_credit``                                          |
+--------------+-----------------+--------------------------------------------------------------------+
| customer_ids | list of integer | Filter on a selection of customers.                                |
|              |                 |                                                                    |
|              |                 | If empty, returns all customers.                                   |
+--------------+-----------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a dictionnary indexed by customer_ids given in parameters.

..  code-block:: python

    {'customer_id1': credit1,
     'customer_id2': credit2,
     ...
     }

Python call example
-------------------
..  code-block:: python
   :linenos:

    credits = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'check_customer_credit',
        [1, 5, 7]
        )
    print credits
    {1: 230, 5: 550, 7: 0}

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    //TODO
    

