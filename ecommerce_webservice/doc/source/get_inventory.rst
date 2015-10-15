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
| shop_ident  | string          | Shop identifier                                                    |
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
        'shop_identifier',
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
 
    <?php 
    
    require_once('ripcord/ripcord.php');
    
    $url = 'http://localhost:8069';
    $db = 'database';
    $username = "admin";
    $password = "admin";
    $shop_identifier = "cafebabe";
    
    
    $common = ripcord::client($url."/xmlrpc/common");
    
    $uid = $common->authenticate($db, $username, $password, array());
    
    $models = ripcord::client("$url/xmlrpc/object");
    
    $product_ids = array(17, 25);
    
    $records = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'get_inventory', array($shop_identifier, $product_ids));
    
    var_dump($records);
    
    ?>


