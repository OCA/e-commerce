# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Website Sale - Price Tiers',
    'summary': 'Add price tier radio buttons to product pages in website shop',
    'version': '10.0.1.1.1',
    'category': 'E-commerce',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'static/src/xml/website_sale_price_tier.xml',
        'templates/assets.xml',
        'wizards/website_config_settings.xml',
    ],
    'demo': [
        'demo/account_tax.xml',
        'demo/product_product.xml',
        'demo/product_pricelist_item.xml',
    ]
}
