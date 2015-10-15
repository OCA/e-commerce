Details of get_docs() method
=======================================

Goal
----

Render a PDF and return it. It can print the sales order's report, invoice's report or delivery order's report.

Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+---------------+-----------------+--------------------------------------------------------------------+
| Argument      | Type            | Comment                                                            |
+===============+=================+====================================================================+
| dbname        | string          | name of the database                                               |
+---------------+-----------------+--------------------------------------------------------------------+
| uid           | integer         | Id of the user making the call                                     |
+---------------+-----------------+--------------------------------------------------------------------+
| password      | string          | password of the user uid                                           |
+---------------+-----------------+--------------------------------------------------------------------+
| model         | string          | Always ``ecommerce.api.v1``                                        |
+---------------+-----------------+--------------------------------------------------------------------+
| method_name   | string          | ``get_docs``                                                       |
+---------------+-----------------+--------------------------------------------------------------------+
| shop_ident    | string          | Shop identifier                                                    |
+---------------+-----------------+--------------------------------------------------------------------+
| sale_id       | integer         | ID of the sales order                                              |
+---------------+-----------------+--------------------------------------------------------------------+
| document_type | string          | ``sale.order`` or ``account.invoice`` or ``stock.picking``.        |
+---------------+-----------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a base64 string for ``sale_id`` and ``document_type`` given in parameters.

..  code-block:: python

    JVBERi0xLjQNCiWTjIueIFJlcG9ydExhYiBH...

Python call example
-------------------
..  code-block:: python
   :linenos:

    sale_doc = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'get_docs',
        'shop_identifier',
        10,
        'sale.order'
        )
    print sale_doc
    JVBERi0xLjQNCiWTjIueIFJlcG9ydExhYiBH...

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
    
    $sale_id = 17;
    
    $document_type = "sale.order";
    //$document_type = "account.invoice";
    //$document_type = "stock.picking";
    
    $records = $models->execute_kw($db, $uid, $password,
        'ecommerce.api.v1', 'get_docs', array($shop_identifier, $sale_id, $document_type));
    
    //var_dump($records);
    
    // data is encoded in base64
    // to be able to read the PDF, we must decode it
    echo base64_decode($records);
    
    ?>
    

