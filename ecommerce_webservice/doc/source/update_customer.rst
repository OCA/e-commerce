Details of update_customer() method
===========================================

Goal
----

Update all customer given in parameter (list of ID) in OpenERP giving necessary fields values

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
| method_name  | string          | ``update_customer``                                                |
+--------------+-----------------+--------------------------------------------------------------------+
| shop_ident   | string          | Shop identifier                                                    |
+--------------+-----------------+--------------------------------------------------------------------+
| customer_ids | list of integer | List of customer's ID we want to update                            |
+--------------+-----------------+--------------------------------------------------------------------+
| values       | dictionnary     | See below for details.                                             |
|              | of values       |                                                                    |
+--------------+-----------------+--------------------------------------------------------------------+

Values parameters
*****************

.. csv-table::
   :header: Name,Type,Comment,Required,Extra Infos
   
    name,string,Name,TRUE,size=128
    active,boolean,Active?,FALSE,default=True
    street,string,Street,FALSE,size=128
    street2,string,Street2,FALSE,size=128
    city,string,City,FALSE,size=128
    zip,string,ZIP,FALSE,size=24
    country,string,Country Code,FALSE,size=2
    phone,string,Phone,FALSE,size=64
    mobile,string,Mobile,FALSE,size=64
    fax,string,Fax,FALSE,size=64
    email,string,email,FALSE,size=240
    website,string,Website URL,FALSE,size=64
    ref,string,Customer code,FALSE,size=64
    comment,string,Comments (text),FALSE,

Return values
^^^^^^^^^^^^^

Method returns True if all customers have been modified. Else it returns an error.

..  code-block:: python

    True

Python call example
-------------------
..  code-block:: python
   :linenos:

    client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'update_customer',
        'shop_identifier',
        [partner_id],
        {'name': 'Janet Doe'}
        )

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    <?php 
    
    require_once('ripcord/ripcord.php');
    
    // CREATE A CUSTOMER AND THEN UPDATE SOME FIELDS
    // FOR THIS NEWLY CREATED CUSTOMER
    
    $url = 'http://localhost:8069';
    $db = 'database';
    $username = "admin";
    $password = "admin";
    $shop_identifier = "cafebabe";
    
    
    $common = ripcord::client($url."/xmlrpc/common");
    
    $uid = $common->authenticate($db, $username, $password, array());
    
    $models = ripcord::client("$url/xmlrpc/object");
    
    $vals_create = array(
        'name'=>'Customer2',
        );
    
    $records = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'create_customer', array($shop_identifier, $vals_create));
    
    
    
    $vals = array(
        'street'=>'street',
        'street2'=>'street2',
        );
    
    $customer_ids = array($records);
    
    $records2 = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'update_customer', array($shop_identifier, $customer_ids, $vals));
    
    var_dump($records);
    
    ?>

