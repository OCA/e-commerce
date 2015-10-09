Details of get_docs() method
=======================================

Goal
----

Render a PDF and return it. It can print the sales order's report, invoice's report or delivery order's report.

If a sales order has several invoices or delivery orders, it returns *all* the pdf documents.

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
| sale_id       | integer         | ID of the sales order                                              |
+---------------+-----------------+--------------------------------------------------------------------+
| document_type | string          | ``sale.order`` or ``account.invoice`` or ``stock.picking``.        |
+---------------+-----------------+--------------------------------------------------------------------+

Return values
^^^^^^^^^^^^^

Method returns a dictionnary indexed by document name for document attached to ``sale_id`` and ``document_type`` given in parameters.

..  code-block:: python

    [{doc_name1: content1},
     {doc_name2: content2},
     ...
     ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    sale_docs = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'get_docs',
        10,
        'sale.order'
        )
    print sale_docs
    [{doc_name: content}, ...]

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    //TODO
    

