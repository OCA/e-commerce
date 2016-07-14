[![License: AGPL-3](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)

============================
Website Sale Google Shopping
============================

Description
===========

This module provides a feed of products from your e-commerce to allow Google Shopping index them and show as search results.

Installation
============

To install this module, you need to:

 * git clone https://github.com/OCA/e-commerce.git --branch 8.0
 * git clone https://github.com/OCA/product-attribute.git --branch 8.0
 * make them available to odoo by adding their locations to the addons_path in
   /etc/odoo-server.conf

Configuration
=============

To configure this module, you need to:

 * no configuration required

Usage
=====

Visit the feed page at http://yourdomain/google-shopping.xml

To use this module succefully, you need to known some aspects:

- Each kind of product has different requirements attributes. The requirements depend of specific google category and your target country.
- Usual product with detailed product attributes are: clothes(color, material, and size), furniture(material, pattern, and color), electronic devices(color) and toy(group of ages).

How to complete product attributes?

- Sales, product sheet, sales tab, website field: Here, you will find all field related to google shopping feed.

A very common mistake is not immediately view the content introduced into the feed xml resultant. Please , check in Settings / web paragraph settings / feed expiry time.
Change the value of Feed expiry time to 0 to see the changes.

Products feed attributes and your localization
-----------------------------------------
Each table header shows where are the attributes to fill them and which attributes are required.

<table>
    <thead>
        <tr>
            <th>Attribute</th>
            <th>Field/description</th>
            <th>Required</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td colspan="3"><em>Sales > Products > Products > Product Template</em></td>
        </tr>
        <tr>
            <td>title</td>
            <td>Product template name with variant attribute names and values if exists</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>brand</td>
            <td>Product brand</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>price</td>
            <td>Sale price</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>gtin</td>
            <td>EAN13 Barcode</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>link</td>
            <td>Default URL directly linking to your item's page on your website</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>image_link</td>
            <td>Default image link to template image (size can be changed in Settings > configuration > website settings)</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td colspan="3"><em>Sales > Products > Products > Product Template > Inventory tab</em></td>
        </tr>
        <tr>
            <td>availability</td>
            <td>Takes a value from virtual stock and automaticly shows: preorder, In stock, out of stock </td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>shipping_weight</td>
            <td>Gross weight</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td colspan="3"><em>Sales > Pricelists > Pricelist Versions</em></td>
        </tr>
        <tr>
            <td>sale_price_effective_date</td>
            <td>Google Shopping date start and Google Shopping date end. Set the date to display the price of products</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td colspan="3"><em>Sales > Products > Products > Product Template > Sales tab</em></td>
        </tr>
        <tr>
            <td>product_type</td>
            <td>Public Category: Own category</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td>color</td>
            <td>Assign an attribute to color attribute that exists in product variants</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td>size</td>
            <td>Assign an attribute to size attribute that exists in product variants</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td>google_product_category</td>
            <td>Google's category of the item</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>condition</td>
            <td>Condition or state of the item: new,refurbished, used</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>gender</td>
            <td>Male, Female, Unisex</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td>Age group</td>
            <td>Newborn, infant, toddler, kids, adult</td>
            <td class="text-center"></td>
        </tr>
        <tr>
            <td>description</td>
            <td>Description for quotations</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td colspan="3"><em>Settings > Configuration > Website Settings</em></td>
        </tr>
        <tr>
            <td>Feed expiry time</td>
            <td>Time to keep caching the feed</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>image size</td>
            <td>Different sizes</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>Use shipping</td>
            <td>Specifying default shipping values in your Google Merchant Center account settings, or by providing this attribute</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>Shipping country</td>
            <td>Shipping country</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>Shipping service</td>
            <td>Shipping service</td>
            <td class="text-center">x</td>
        </tr>
        <tr>
            <td>Shipping price</td>
            <td>Shipping price</td>
            <td class="text-center">x</td>
        </tr>
    </tbody>
</table>


All info-->:https://support.google.com/merchants/answer/1344057

**Pay Attention**

> **All product without the attributes required by Google Merchant will not be able to be indexed in google shopping.**

**And now:**

[![TryMe](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)]()

Known issues / Roadmap
======================
* Add 'google_mpn' field to Product Template and Product Variant views
* Allow to set additional images from product gallery for 'additional_image_link' tag
* Include specific product atributtes in erp and xml(patterns)
* Unit pricing (unit pricing measure, unit pricing base measure)
* Energetic calification labels (only UE and Switzerland)

Google Merchant Center Help:
=============================
**Products Feed Specification**

https://support.google.com/merchants/answer/188494

**Troubleshooting:**

https://support.google.com/merchants/answer/160161

**Categorize your products:**

https://support.google.com/merchants/answer/1705911

Contributors
------------

* Jorge Camacho <jcamacho@trey.es>
* Abraham González <abraham@trey.es>

Maintainer
----------

[![Logo](https://odoo-community.org/logo.png)](https://odoo-community.org)

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
