Products Template API Details
=============================

Goal
----

Return information about all product variants. The search can be filtered by search criteria and the returned information can be limited to a selection of fields.

If the eshop does not care about product templates, this is the only method that it will use for the products, because the returned data includes the data of the template of the variant as well.

Specification
-------------

Call
^^^^

It takes the following arguments in the order of the rows:

+-------------+------------------------+---------------------------------------------------------------------+
| Argument    | Type                   | Comment                                                             |
+=============+========================+=====================================================================+
| dbname      | string                 | name of the database                                                |
+-------------+------------------------+---------------------------------------------------------------------+
| uid         | integer                | Id of the user making the call                                      |
+-------------+------------------------+---------------------------------------------------------------------+
| password    | string                 | password of the user uid                                            |
+-------------+------------------------+---------------------------------------------------------------------+
| model       | string                 | Always ``ecommerce.api.v1``                                         |
+-------------+------------------------+---------------------------------------------------------------------+
| method_name | string                 | ``search_read_product_template``                                    |
+-------------+------------------------+---------------------------------------------------------------------+
| shop_ident  | string                 | Shop identifier                                                     |
+-------------+------------------------+---------------------------------------------------------------------+
| domain      | list of tuples/strings | Search domain. See :doc:`_about_search_domains` chapter.            |
|             |                        |                                                                     |
|             |                        | Example: ``['sku = ABC']`` or ``[('sku', '=', 'ABC')]``             |
+-------------+------------------------+---------------------------------------------------------------------+
| fields      | list of strings        | If provided, the response returns only the asked fields.            |
|             |                        |                                                                     |
|             |                        | Example: ``['id', 'name', 'description']``                          |
|             |                        |                                                                     |
|             |                        | Otherwise, it will return all fields in ``product.template`` object |
+-------------+------------------------+---------------------------------------------------------------------+
| offset      | integer                | Set an offset for reading rows                                      |
+-------------+------------------------+---------------------------------------------------------------------+
| limit       | integer                | Limit number of returned rows                                       |
+-------------+------------------------+---------------------------------------------------------------------+
| order       | string                 | Change ordering of rows (example : ``'create_date asc'``)           |
+-------------+------------------------+---------------------------------------------------------------------+

Available Fields
----------------

.. csv-table::
   :header: "name", "field description", "type", "available values", "required", "size", "translate", "standard/custom", "help"

    categ_id,Category,FK to product.category object,,TRUE,,FALSE,standard,
    company_id,Company,FK to res.company object,,FALSE,,FALSE,standard,
    cost_method,Costing Method,selection,"('standard','Standard Price'),
    ('average','Average Price')",TRUE,,FALSE,standard,"Standard Price: The cost price is manually updated at the end of a specific period (usually every year).
    Average Price: The cost price is recomputed at each incoming shipment."
    description,Description,text,,FALSE,,TRUE,standard,
    description_purchase,Purchase Description,text,,FALSE,,TRUE,standard,
    description_sale,Sale Description,text,,FALSE,,TRUE,standard,
    list_price,Sale Price,float,,FALSE,,FALSE,standard,
    loc_case,Case,char,,FALSE,16,FALSE,standard,
    loc_rack,Rack,char,,FALSE,16,FALSE,standard,
    loc_row,Row,char,,FALSE,16,FALSE,standard,
    mes_type,Measure Type,selection,,FALSE,,FALSE,standard,
    name,Name,char,,TRUE,128,TRUE,standard,
    procure_method,Procurement Method,selection,"('make_to_stock','Make to Stock'),
    ('make_to_order','Make to Order')",FALSE,,FALSE,standard,"Make to Stock: When needed, the product is taken from the stock or we wait for replenishment.
    Make to Order: When needed, the product is purchased or produced."
    produce_delay,Manufacturing Lead Time,float,,FALSE,,FALSE,standard,
    product_manager,Product Manager,FK to res.users object,,FALSE,,FALSE,standard,
    property_account_expense,Expense Account,FK to account.account object,,FALSE,,FALSE,standard,
    property_account_income,Income Account,FK to account.account object,,FALSE,,FALSE,standard,
    property_stock_account_input,Stock Input Account,FK to account.account object,,FALSE,,FALSE,standard,
    property_stock_account_output,Stock Output Account,FK to account.account object,,FALSE,,FALSE,standard,
    property_stock_inventory,Inventory Location,FK to stock.location object,,FALSE,,FALSE,standard,
    property_stock_procurement,Procurement Location,FK to stock.location object,,FALSE,,FALSE,standard,
    property_stock_production,Production Location,FK to stock.location object,,FALSE,,FALSE,standard,
    rental,Can be Rent,boolean,,FALSE,,FALSE,standard,
    sale_delay,Customer Lead Time,float,,FALSE,,FALSE,standard,
    sale_ok,Can be Sold,boolean,,FALSE,,FALSE,standard,
    seller_ids,Supplier,one2many,,FALSE,,FALSE,standard,sellers list with prices
    standard_price,Cost,float,,FALSE,,FALSE,standard,
    state,Status,selection,"('',''),
    ('draft', 'In Development'),
    ('sellable','Normal'),
    ('end','End of Lifecycle'),
    ('obsolete','Obsolete')",FALSE,,FALSE,standard,
    supplier_taxes_id,Supplier Taxes,0 to N relation between product.template and account.tax,,FALSE,,FALSE,standard,
    supply_method,Supply Method,selection,"('produce','Manufacture'),
    ('buy','Buy')",FALSE,,FALSE,standard,"Manufacture: When procuring the product, a manufacturing order or a task will be generated, depending on the product type.
    Buy: When procuring the product, a purchase order will be generated."
    taxes_id,Customer Taxes,0 to N relation between product.template and account.tax,,FALSE,,FALSE,standard,
    type,Product Type,selection,"('product','Stockable Product'),
    ('consu', 'Consumable'),
    ('service','Service')",TRUE,,FALSE,standard,"Consumable: Will not imply stock management for this product.
    Stockable product: Will imply stock management for this product."
    uom_id,Unit of Measure,FK to product.uom object,,TRUE,,FALSE,standard,
    uom_po_id,Purchase Unit of Measure,FK to product.uom object,,TRUE,,FALSE,standard,
    uos_coeff,Unit of Measure -> UOS Coeff,float,,FALSE,,FALSE,standard,
    uos_id,Unit of Sale,FK to product.uom object,,FALSE,,FALSE,standard,
    volume,Volume,float,,FALSE,,FALSE,standard,
    warranty,Warranty,float,,FALSE,,FALSE,standard,
    weight,Gross Weight,float,,FALSE,,FALSE,standard,
    weight_net,Net Weight,float,,FALSE,,FALSE,standard,

Note: If an Odoo module adds fields, they will automatically be added to the API return.


Return values
^^^^^^^^^^^^^

Method returns a list of dictionnary. Each dictionnary corresponds to a product template matching domain criterion.

..  code-block:: python

     [
      {'id': 15, 'name': 'T-Shirt', 'default_code': 'ABC', ...},
      {'id': 16, 'name': 'Hat', 'default_code': 'DEF', ...},
       ...
      ]

Python call example
-------------------
..  code-block:: python
   :linenos:

    templates = client.execute(
        dbname, uid, pwd,
        'ecommerce.api.v1',
        'search_read_product_variant',
        'shop_identifier',
        ['sku = ABC', 'create_date > 2015-09-24 00:00:00']
        )
    print templates
    [{'id': 15, 'name': 'T-Shirt', 'default_code': 'ABC', ...}, ...]

PHP call example
----------------

 ..  code-block:: php
    :linenos:
 
    <?php 
    
    // TODO
    
    ?>


