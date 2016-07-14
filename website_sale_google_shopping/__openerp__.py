# -*- coding: utf-8 -*-
# © 2016 Trey, Kilobytes de Soluciones SL (Granada, Spain, http://www.trey.es)
#        Jorge Camacho <jcamacho@trey.es>
#        Abraham González <abraham@trey.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Google Shopping',
    'category': 'e-commerce',
    'summary': 'Generate products feed for Google Merchant Center',
    'version': '8.0.1.0.0',
    'author': 'Trey, Kilobytes de Soluciones S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.trey.es',
    'depends': [
        'product_brand',
        'stock',
        'website_sale',
    ],
    'post_init_hook': 'post_init_hook',
    'data': [
        'views/product.xml',
        'views/pricelist.xml',
        'views/website_config_settings.xml',
        'views/website.xml',
        'views/google_product_category.xml',
        'views/website_sale_google_shopping.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
